#!/usr/bin/env python3
"""Record the component gallery previews (preview.gif + thumbnail.png).

Each component's preview app is served with `shiny run`, driven by a short
scripted interaction in headless Chromium, and captured with the CDP
screencast. Frames are resampled to a constant 50 fps and encoded with ffmpeg.
thumbnail.png is the GIF's exact first frame, so hover swaps are seamless.

Every preview is laid out in the gallery card's 450x253 frame. `zoom` scales
the app inside that frame (the viewport becomes 450/zoom x 253/zoom CSS px), so
text renders at the same size across cards unless a component needs the room.

    uv run python scripts/record-component-previews.py            # all
    uv run python scripts/record-component-previews.py slider toolbar
"""

from __future__ import annotations

import argparse
import asyncio
import base64
import json
import math
import re
import shutil
import socket
import subprocess
import sys
import tempfile
import time
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path
from typing import Awaitable, Callable

from PIL import Image
from playwright.async_api import Page, async_playwright

ROOT = Path(__file__).resolve().parent.parent
COMPONENTS = ROOT / "components"

WIDTH, HEIGHT = 450, 253  # gallery card frame (CSS px)
FPS = 50  # 20 ms GIF frame delay; browsers honor it (<= 10 ms is clamped)
ZOOM = 2.0  # default: 16px body text renders at 32px in the 450px frame
BLUE = "#007bc2"  # Shiny's primary color

# Pin every system-derived color (macOS accent color leaks into focus rings,
# checked <option>s and text selection) and hide scrollbars.
CSS = f"""
:root {{ accent-color: {BLUE}; }}
html, body {{ overflow: hidden !important; scrollbar-width: none; }}
::-webkit-scrollbar {{ display: none; }}
*:focus-visible {{ outline-color: {BLUE} !important; }}
::selection {{ background: rgba(0, 123, 194, 0.25); }}
.form-check-label, .control-label, .btn {{ white-space: nowrap; }}
select option:checked {{
  background: {BLUE} linear-gradient({BLUE}, {BLUE}) !important;
  color: #fff !important;
}}
"""


class Driver:
    """Mouse/keyboard helpers that move in real time so motion is smooth."""

    def __init__(self, page: Page):
        self.page = page
        self.x, self.y = 0.0, 0.0
        self.poster_time: float | None = None

    def poster(self):
        """Mark the current state as the static thumbnail (and GIF start)."""
        self.poster_time = time.time()

    async def wait(self, ms: float):
        await asyncio.sleep(ms / 1000)

    async def center(self, selector: str, dx: float = 0.5, dy: float = 0.5):
        box = await self.page.locator(selector).first.bounding_box()
        assert box, f"{selector} is not visible"
        return box["x"] + box["width"] * dx, box["y"] + box["height"] * dy

    async def glide(self, x: float, y: float, ms: float = 450):
        # Paced by the clock and not awaited one by one: an awaited move waits
        # for the renderer, which would stretch a drag and drop frames.
        x0, y0 = self.x, self.y
        start = time.perf_counter()
        pending = []
        while True:
            t = min(1.0, (time.perf_counter() - start) * 1000 / ms)
            e = t * t * (3 - 2 * t)  # smoothstep ease-in-out
            pending.append(
                asyncio.ensure_future(
                    self.page.mouse.move(x0 + (x - x0) * e, y0 + (y - y0) * e)
                )
            )
            if t >= 1:
                break
            await asyncio.sleep(1 / 60)
        await asyncio.gather(*pending)
        self.x, self.y = x, y

    async def hover(self, selector: str, ms: float = 450, **kw):
        await self.glide(*await self.center(selector, **kw), ms=ms)

    async def click(self, selector: str | None = None, ms: float = 450, **kw):
        if selector:
            await self.hover(selector, ms=ms, **kw)
        await self.page.mouse.down()
        await asyncio.sleep(0.09)
        await self.page.mouse.up()

    async def drag_to(self, x: float, y: float, ms: float = 700):
        # CDP input tops out near 25 fps mid-drag, so the moves between press
        # and release are dispatched in-page, once per animation frame.
        await self.page.mouse.down()
        await self.page.evaluate(
            """([x0, y0, x1, y1, ms]) => new Promise((done) => {
              const start = performance.now();
              const step = (now) => {
                const t = Math.min(1, (now - start) / ms), e = t * t * (3 - 2 * t);
                const x = x0 + (x1 - x0) * e, y = y0 + (y1 - y0) * e;
                const target = document.elementFromPoint(x, y) || document;
                target.dispatchEvent(new MouseEvent("mousemove", {
                  bubbles: true, clientX: x, clientY: y, buttons: 1 }));
                t < 1 ? requestAnimationFrame(step) : done();
              };
              requestAnimationFrame(step);
            })""",
            [self.x, self.y, x, y, ms],
        )
        await self.page.mouse.move(x, y)
        await self.page.mouse.up()
        self.x, self.y = x, y

    async def type(self, text: str, delay: float = 75):
        for ch in text:
            await self.page.keyboard.type(ch)
            await asyncio.sleep(delay / 1000)

    async def press(self, key: str, pause: float = 350):
        await self.page.keyboard.press(key)
        await asyncio.sleep(pause / 1000)

    async def idle(self, ms: float = 250):
        """Wait until Shiny has finished recalculating outputs."""
        await self.page.wait_for_function(
            "() => !document.documentElement.classList.contains('shiny-busy')"
        )
        await asyncio.sleep(ms / 1000)


Play = Callable[[Driver], Awaitable[None]]


@dataclass
class Spec:
    play: Play
    app: str = "app-preview.py"
    zoom: float = ZOOM
    css: str = ""
    ready: str = ""  # selector to wait for before recording starts
    files: dict[str, str] = field(default_factory=dict)  # extra files for app dir


SPECS: dict[str, Spec] = {}


def spec(path: str, **kw):
    def register(play: Play):
        SPECS[path] = Spec(play=play, **kw)
        return play

    return register


# ---------------------------------------------------------------------------
# Scenarios


# Layout helpers: pin content to a region of the frame (overrides the
# preview apps' "vh-100 d-flex ... align-items-center" wrapper).
TOP = ".vh-100 { align-items: flex-start !important; padding-top: 14px; }"
PAD = "body { padding: 12px 16px !important; } .container-fluid { padding: 0; }"


def clicker(selector: str, times: int = 2, gap: float = 500):
    async def play(d: Driver):
        for _ in range(times):
            await d.click(selector)
            await d.wait(gap)
        await d.glide(d.x + 120, d.y + 70)
        await d.idle(300)

    return play


def slider(container: str = "", fracs=(0.85, 0.2, None), idle: bool = False):
    """Drag a slider handle to fractions of its track; None returns home."""

    async def play(d: Driver):
        handle = f"{container} .irs-handle".strip()
        await d.hover(handle, ms=500)
        home = d.x
        line = await d.page.locator(f"{container} .irs-line".strip()).bounding_box()
        for f in fracs:
            x = home if f is None else line["x"] + line["width"] * f
            await d.drag_to(x, d.y, ms=750)
            await (d.idle(350) if idle else d.wait(300))

    return play


def typer(selector: str, text: str, submit: str | None = None, poster=False):
    async def play(d: Driver):
        await d.click(selector)
        await d.wait(200)
        await d.type(text)
        await d.wait(300)
        if poster:
            d.poster()
        if submit:
            await d.press(submit)
        await d.idle(700)

    return play


spec("inputs/action-button")(clicker("#action_button"))
spec("inputs/action-link")(clicker("#action_link"))
spec("inputs/task-button", zoom=2.0)(clicker("#task_button", times=1, gap=2000))
spec("inputs/bookmark-button")(clicker(".btn", times=1))
spec("inputs/download-button")(clicker("#download", times=1))
spec("inputs/download-link")(clicker("#download", times=1))
spec("inputs/slider")(slider())


@spec("inputs/slider-range")
async def _(d: Driver):
    line = await d.page.locator(".irs-line").bounding_box()
    for handle, fracs in ((".irs-handle.to", (0.92, 0.7)), (".irs-handle.from", (0.08, 0.25))):
        await d.hover(handle, ms=450)
        for f in fracs:
            await d.drag_to(line["x"] + line["width"] * f, d.y, ms=700)
            await d.wait(250)


@spec("inputs/checkbox", zoom=1.8)
async def _(d: Driver):
    for i in range(2):
        await d.click("#x", ms=400)
        await d.wait(550)
        if i == 0:
            d.poster()


@spec("inputs/switch", zoom=1.8)
async def _(d: Driver):
    for _ in range(2):
        await d.click("#switch", ms=400)
        await d.wait(600)


@spec("inputs/checkbox-group")
async def _(d: Driver):
    for v in ("a", "b", "a", "b"):
        await d.click(f"input[value='{v}']", ms=350)
        await d.wait(400)


@spec("inputs/radio-buttons")
async def _(d: Driver):
    for v in ("2", "1"):
        await d.click(f"input[value='{v}']", ms=400)
        await d.wait(600)


@spec("inputs/dark-mode", zoom=3.0)
async def _(d: Driver):
    for _ in range(2):
        await d.click("bslib-input-dark-mode", ms=400)
        await d.wait(900)


spec("inputs/text-box")(typer("#x", "Hello, Shiny!"))
spec("inputs/password-field")(typer("#x", "hunter2hunter2", poster=True))
spec("inputs/text-area", zoom=1.8)(typer("#x", "Shiny for Python\nmakes apps easy."))
@spec("inputs/submit-textarea", zoom=1.6)
async def _(d: Driver):
    await typer("textarea", "Hello, Shiny!")(d)
    await d.click("button", ms=450)
    await d.idle(900)


@spec("inputs/numeric-input")
async def _(d: Driver):
    await d.click("#x")
    for key in ["ArrowUp"] * 4 + ["ArrowDown"] * 4:
        await d.press(key, pause=220)
    await d.idle(300)


@spec("inputs/code-editor", zoom=1.3)
async def _(d: Driver):
    await d.click(".prism-code-editor, textarea", dx=0.95, dy=0.85)
    await d.press("End", 100)
    await d.type("\n\ngreet('Shiny')", delay=70)
    await d.wait(500)


# Native <select> popups are drawn by the OS and never reach the page, so step
# through the options programmatically instead.
async def step_select(d: Driver, selector: str, values: list[str]):
    await d.click(selector)
    await d.page.keyboard.press("Escape")
    for v in values:
        await d.wait(650)
        await d.page.select_option(selector, v)
    await d.wait(500)


# Chrome's customizable select draws the picker in the page's top layer, so
# unlike the OS popup it shows up in the capture.
BASE_SELECT = """
select.form-select, select.form-select::picker(select) { appearance: base-select; }
select.form-select::picker(select) { border: 1px solid #dee2e6; border-radius: 6px;
  box-shadow: 0 6px 16px rgba(0,0,0,.12); padding: 4px 0; }
select.form-select::picker-icon { display: none; }
select.form-select option { padding: 2px 14px; }
select.form-select option::checkmark { display: none; }
select.form-select option:hover { background: #e9ecef; }
select.form-select optgroup { font-weight: 600; padding: 2px 8px; }
"""


@spec("inputs/select-single", zoom=1.45, css=TOP + BASE_SELECT)
async def _(d: Driver):
    for v in ("1B", "1C"):
        await d.click("#select", ms=450)
        await d.wait(450)
        await d.hover(f"option[value='{v}']", ms=400)
        await d.wait(250)
        await d.click()
        await d.wait(650)


@spec("inputs/select-multiple", zoom=1.6)
async def _(d: Driver):
    await d.click("option[value='1A']", ms=400)
    for v in ("1C", "1B"):
        await d.wait(450)
        await d.hover(f"option[value='{v}']", ms=350)
        await d.page.keyboard.down("Meta")
        await d.click()
        await d.page.keyboard.up("Meta")
    await d.wait(600)
    await d.click("option[value='1A']", ms=400)


SELECTIZE = TOP + " .selectize-dropdown-content { max-height: 7.2em !important; }"


@spec("inputs/selectize-single", zoom=1.45, css=SELECTIZE)
async def _(d: Driver):
    await d.click(".selectize-input", ms=400)
    for v in ("1B", "1C"):
        await d.wait(350)
        await d.hover(f".option[data-value='{v}']", ms=300)
    await d.wait(300)
    await d.click()
    await d.wait(900)


@spec("inputs/selectize-multiple", zoom=1.45, css=SELECTIZE)
async def _(d: Driver):
    await d.click(".selectize-input", ms=400)
    for v in ("1A", "1C", "1B"):
        await d.wait(400)
        await d.click(f".option[data-value='{v}']", ms=300)
    await d.wait(300)
    await d.page.keyboard.press("Escape")
    await d.wait(400)
    d.poster()
    await d.wait(300)


# bootstrap-datepicker drops the calendar below the input; park it to the
# right instead so the input and calendar both fit the 16:9 frame.
DATEPICKER = """
.vh-100 { justify-content: flex-start !important; align-items: center !important;
  flex-direction: row !important; }
.datepicker.dropdown-menu { top: 50% !important; left: auto !important;
  right: 14px; transform: translateY(-50%); }
.datepicker-dropdown::before, .datepicker-dropdown::after { display: none; }
"""


async def pick_dates(d: Driver, inputs: list[tuple[str, str]], poster: int):
    """Pick each (input, day); the thumbnail shows input `poster`'s calendar."""
    for i, (selector, day) in enumerate(inputs):
        await d.click(selector, ms=400)
        await d.wait(450)
        if i == poster:
            d.poster()
        await d.click(
            f".datepicker-days td.day:not(.old):not(.new):text-is('{day}')", ms=450
        )
        await d.wait(450)
    await d.glide(d.x, d.y + 60)


@spec("inputs/date-selector", zoom=1.0, css=DATEPICKER + ".form-group{width:170px!important}")
async def _(d: Driver):
    await pick_dates(d, [("#x", "12")], poster=0)


@spec(
    "inputs/date-range-selector",
    zoom=1.0,
    css=DATEPICKER
    + ".form-group{width:170px!important} .input-daterange{flex-direction:column}"
    " .input-daterange > *{width:100%!important;border-radius:var(--bs-border-radius)!important}"
    " .input-daterange .input-group-text{border:0!important;background:none!important;padding:2px;"
    "justify-content:center;width:100%}",
)
async def _(d: Driver):
    await pick_dates(
        d, [("#x input:first-of-type", "9"), ("#x input:last-of-type", "20")], poster=1
    )


CSV = "species,island,mass\nAdelie,Torgersen,3750\nGentoo,Biscoe,5000\n"


@spec("inputs/file", zoom=1.35)
async def _(d: Driver):
    await d.hover(".btn-file", ms=450)
    await d.wait(300)
    await d.page.locator("input[type=file]").set_input_files(
        files=[{"name": "penguins.csv", "mimeType": "text/csv", "buffer": CSV.encode()}]
    )
    await d.idle(900)
    d.poster()
    await d.wait(300)




@spec("inputs/toolbar-button", zoom=1.6)
async def _(d: Driver):
    for sel in ("#refresh", "#save"):
        await d.hover(sel, ms=450)
        await d.wait(900)
        await d.click()
        await d.wait(250)
    await d.glide(d.x - 80, d.y + 70)


@spec("inputs/toolbar-select", zoom=1.6)
async def _(d: Driver):
    await step_select(d, "#filter select", ["Active", "Archived", "All"])


@spec("layout/toolbar", zoom=1.6)
async def _(d: Driver):
    await d.hover("#action1", ms=450)
    await d.wait(700)
    await d.click()
    await step_select(d, "#options select", ["CDE", "EFG", "ABC"])


# --- display messages -------------------------------------------------------


@spec("display-messages/chat", zoom=1.1, css="body > .container-fluid > h2, .bslib-page-fill > h2 { display: none; }")
async def _(d: Driver):
    await typer("[role=textbox]", "Hello, Shiny!", "Enter")(d)
    await d.wait(600)


@spec("display-messages/notifications", zoom=1.35)
async def _(d: Driver):
    for i in range(2):
        await d.click("#show", ms=400)
        await d.wait(700)
        if i == 0:
            d.poster()
    await d.glide(d.x - 60, d.y + 50)


@spec("display-messages/progress-bar", zoom=1.35)
async def _(d: Driver):
    await d.click("#button")
    await d.wait(800)
    d.poster()
    await d.idle(800)


@spec("display-messages/toasts", zoom=1.35)
async def _(d: Driver):
    await d.click("#show")
    await d.wait(700)
    d.poster()
    await d.wait(900)


@spec("display-messages/popovers", zoom=1.35, css=".vh-100{align-items:flex-end!important;padding-bottom:28px}")
async def _(d: Driver):
    await d.click("#btn")
    await d.wait(600)
    d.poster()
    await d.wait(700)
    await d.click("#btn")
    await d.wait(500)


@spec("display-messages/tooltips", zoom=1.6, css=".vh-100{align-items:flex-end!important;padding-bottom:22px}")
async def _(d: Driver):
    await d.hover("#tooltip")
    await d.wait(700)
    d.poster()
    await d.wait(700)
    await d.glide(d.x + 150, d.y + 60)
    await d.wait(400)


# --- layout -----------------------------------------------------------------


@spec("layout/accordion", zoom=1.1)
async def _(d: Driver):
    for i in (1, 2):
        await d.click(f".accordion-item:nth-child({i}) .accordion-button", ms=400)
        await d.wait(700)


@spec("layout/cards", zoom=1.35, css=".card { width: 18rem; }")
async def _(d: Driver):
    await d.hover(".card", ms=450)
    await d.wait(400)
    await d.click(".bslib-full-screen-enter", ms=350)
    await d.wait(1200)
    await d.click(".bslib-full-screen-exit", ms=400)
    await d.wait(600)


@spec("layout/modal", zoom=1.35)
async def _(d: Driver):
    await d.click("#show")
    await d.wait(1400)
    await d.page.keyboard.press("Escape")
    await d.wait(700)


@spec("layout/offcanvas", zoom=1.35)
async def _(d: Driver):
    await d.wait(900)
    await d.click("#open")
    await d.wait(2800)
    await d.click(".offcanvas .btn-close", ms=400)
    await d.wait(700)


# --- outputs ----------------------------------------------------------------


spec("outputs/text", zoom=1.6)(typer("#x", "Shiny preview"))
spec("outputs/verbatim-text", zoom=1.6)(typer("#x", "Shiny preview"))
spec("outputs/code", zoom=1.6)(typer("#message", "Hello, Shiny!"))


@spec("outputs/ui", zoom=1.45, css=".vh-100{padding-top:18px!important}")
async def _(d: Driver):
    await slider(fracs=(0.9, 0.3), idle=True)(d)
    for _ in range(2):
        await d.click("#show_ui", ms=450)
        await d.idle(700)


@spec("outputs/markdown-stream", app="app-detail-preview.py", zoom=0.95, css=PAD)
async def _(d: Driver):
    await d.click("#stream")
    await d.wait(300)
    await d.page.wait_for_function(
        "() => document.body.innerText.includes('Auto-scrolls')"
    )
    await d.wait(600)
    d.poster()


PLOT = PAD + """
.shiny-plot-output, .shiny-ipywidget-output
  { height: calc(100vh - 100px) !important; }
"""

spec("outputs/plot-matplotlib", app="app-core.py", zoom=1.0, css=PLOT)(
    slider(fracs=(0.45, 0.08, None), idle=True)
)
spec("outputs/plot-seaborn", app="app-core.py", zoom=1.0, css=PLOT)(
    slider(fracs=(0.45, 0.08, None), idle=True)
)
@spec("outputs/plot-plotly", app="app-core.py", zoom=1.0, css=PLOT, ready=".js-plotly-plot .bars")
async def _(d: Driver):
    # shinywidgets rebuilds the widget on every change, blanking it for up to a
    # second; let each redraw land before the next drag, and linger at the end.
    await d.hover(".irs-handle", ms=500)
    home = d.x
    line = await d.page.locator(".irs-line").bounding_box()
    for f in (0.45, 0.08, None):
        x = home if f is None else line["x"] + line["width"] * f
        await d.drag_to(x, d.y, ms=750)
        await d.idle(300)
        await d.page.wait_for_selector(".js-plotly-plot .bars")
        await d.wait(700)
    await d.wait(800)
SIDE = PAD + """
.container-fluid { display: grid !important; grid-template-columns: 28% 1fr;
  gap: 18px; align-items: center; height: calc(100vh - 24px); }
.container-fluid > * { margin: 0 !important; min-width: 0; }
"""

spec(
    "outputs/table",
    zoom=1.05,
    css=SIDE + ".table td, .table th { padding: .35rem .5rem; white-space: nowrap; }",
)(
    slider(fracs=(1.0, 0.0, None), idle=True)
)
spec(
    "outputs/table-great-tables",
    app="app-variation-reactive-preview.py",
    zoom=1.0,
    css=SIDE,
)(slider(fracs=(0.55, 0.85, 0.0), idle=True))
spec(
    "outputs/value-box",
    app="app-variation-reactive-value-box-core.py",
    zoom=1.0,
    css=PAD + """
.bslib-grid { grid-template-columns: 1fr 1fr !important; }
.bslib-grid-item { grid-column: auto !important; }
.bslib-grid-item:has(h2) { display: none; }
.bslib-grid-item:has(.shiny-input-container) { grid-column: 1 / -1 !important; }
.shiny-input-container { width: 100% !important; }
""",
)(slider(fracs=(0.8, 0.5, None), idle=True))


@spec(
    "outputs/image",
    app="app-core.py",
    zoom=1.3,
    css=PAD + """
.container-fluid { display: grid !important; grid-template-columns: 1fr 1fr;
  align-items: center; justify-items: center; height: calc(100vh - 24px); }
.container-fluid > * { margin: 0 !important; }
.shiny-image-output, .form-group { width: auto !important; height: auto !important; }""",
)
async def _(d: Driver):
    for _ in range(2):
        await d.click("#show", ms=400)
        await d.idle(600)


GRID = PAD + """h2 { font-size: 1.4rem; }
.shiny-data-grid { max-height: calc(100vh - 78px) !important; }"""


async def grid_play(d: Driver):
    await d.click("th:nth-child(3)", ms=500)
    await d.idle(600)
    await d.click("tbody tr:nth-child(1) td:nth-child(2)", ms=450)
    await d.wait(500)
    await d.hover("tbody tr:nth-child(3) td:nth-child(2)", ms=400)
    await d.page.keyboard.down("Meta")
    await d.click()
    await d.page.keyboard.up("Meta")
    await d.wait(800)


spec("outputs/data-grid", zoom=1.0, css=GRID)(grid_play)
spec("outputs/data-table", zoom=1.0, css=GRID)(grid_play)


@spec(
    "outputs/map-ipyleaflet",
    app="app-core.py",
    zoom=1.0,
    css="body{padding:0!important}.container-fluid{padding:0}"
    ".html-widget-output,.shinywidgets-output,.leaflet-container{height:100vh!important}",
)
async def _(d: Driver):
    await d.wait(800)
    await d.glide(225, 126, ms=300)
    # Panning repaints the whole frame, so keep it short to bound the GIF size.
    await d.drag_to(175, 150, ms=650)
    await d.wait(500)
    await d.drag_to(225, 126, ms=650)
    await d.wait(300)


# ---------------------------------------------------------------------------
# Recording machinery


def unpack_app(src: Path, dest: Path):
    """Copy the component dir, writing the chosen app as app.py.

    Handles shinylive multi-file bundles (`## file: name` headers).
    """
    shutil.copytree(src.parent, dest, ignore=shutil.ignore_patterns("__pycache__"))
    text = src.read_text()
    parts = re.split(r"^## file: (.+)$", text, flags=re.M)
    if len(parts) == 1:
        (dest / "app.py").write_text(text)
        return
    for name, body in zip(parts[1::2], parts[2::2]):
        (dest / name.strip()).write_text(body.strip("\n") + "\n")


def free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def wait_http(url: str, proc: subprocess.Popen, timeout: float = 60):
    deadline = time.time() + timeout
    while time.time() < deadline:
        if proc.poll() is not None:
            raise RuntimeError(f"app exited with {proc.returncode}")
        try:
            urllib.request.urlopen(url, timeout=1)
            return
        except OSError:
            time.sleep(0.2)
    raise TimeoutError(url)


def encode(
    frames: list[tuple[float, bytes]],
    t0: float,
    t1: float,
    poster: float | None,
    out_dir: Path,
):
    """Resample screencast frames to FPS and write preview.gif + thumbnail.png.

    The loop is rotated to start at `poster` (if marked), so the thumbnail can
    show a mid-interaction state while hover still swaps in seamlessly.
    """
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        n = int((t1 - t0) * FPS)
        shift = int((poster - t0) * FPS) if poster else 0
        j = 0
        for i in range(n):
            t = t0 + i / FPS
            while j + 1 < len(frames) and frames[j + 1][0] <= t:
                j += 1
            (tmp / f"{(i - shift) % n:05d}.png").write_bytes(frames[j][1])
        gif = out_dir / "preview.gif"
        subprocess.run(
            [
                "ffmpeg", "-loglevel", "error", "-y",
                "-framerate", str(FPS), "-i", str(tmp / "%05d.png"),
                "-fps_mode", "vfr",
                "-lavfi",
                "mpdecimate=hi=1:lo=1:frac=0:max=-50,"
                f"crop={WIDTH}:{HEIGHT}:0:0,split[a][b];"
                "[a]palettegen=max_colors=256:stats_mode=full[p];"
                "[b][p]paletteuse=dither=none:diff_mode=rectangle",
                "-loop", "0", str(gif),
            ],
            check=True,
        )  # fmt: skip
    with Image.open(gif) as im:
        im.seek(0)
        im.convert("RGB").save(out_dir / "thumbnail.png", optimize=True)


async def record(p, name: str, spec: Spec, out_dir: Path):
    with tempfile.TemporaryDirectory() as tmp:
        app_dir = Path(tmp) / "app"
        unpack_app(out_dir / spec.app, app_dir)
        for fname, body in spec.files.items():
            (app_dir / fname).write_text(body)
        port = free_port()
        proc = subprocess.Popen(
            [sys.executable, "-m", "shiny", "run", "--port", str(port), "app.py"],
            cwd=app_dir,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
        )
        try:
            url = f"http://127.0.0.1:{port}/"
            await asyncio.to_thread(wait_http, url, proc)
            # The screencast ignores emulated DPR and would hand back CSS-px
            # frames, so give the browser a real scale factor instead.
            browser = await p.chromium.launch(
                args=[f"--force-device-scale-factor={spec.zoom}"]
            )
            ctx = await browser.new_context(
                viewport={
                    # Round up and crop in encode(): resampling would blur.
                    "width": math.ceil(WIDTH / spec.zoom),
                    "height": math.ceil(HEIGHT / spec.zoom),
                },
                device_scale_factor=spec.zoom,
                accept_downloads=True,
            )
            # Inject before first paint so outputs are sized by it from the start.
            await ctx.add_init_script(
                "document.addEventListener('DOMContentLoaded', () => {"
                " const s = document.createElement('style');"
                f" s.textContent = {json.dumps(CSS + spec.css)};"
                " document.head.appendChild(s); });"
            )
            page = await ctx.new_page()
            await page.goto(url)
            await page.wait_for_function(
                "() => window.Shiny?.shinyapp?.isConnected()"
            )
            await page.evaluate("document.fonts.ready")
            if spec.ready:
                await page.wait_for_selector(spec.ready)
            d = Driver(page)
            await d.idle(600)

            frames: list[tuple[float, bytes]] = []
            cdp = await ctx.new_cdp_session(page)

            def on_frame(ev):
                frames.append(
                    (ev["metadata"]["timestamp"], base64.b64decode(ev["data"]))
                )
                asyncio.ensure_future(
                    cdp.send("Page.screencastFrameAck", {"sessionId": ev["sessionId"]})
                )

            cdp.on("Page.screencastFrame", on_frame)
            await cdp.send("Page.startScreencast", {"format": "png"})
            # Force a paint so the resting state is captured as frame 0.
            await page.evaluate("document.body.style.transform = 'translateZ(0)'")
            while not frames:
                await asyncio.sleep(0.02)
            t0 = frames[0][0]
            await asyncio.sleep(0.4)
            await spec.play(d)
            await asyncio.sleep(0.8)
            t1 = time.time()  # screencast timestamps are wall-clock seconds
            await cdp.send("Page.stopScreencast")
            await browser.close()
        finally:
            proc.terminate()
            proc.wait()
    encode(frames, t0, t1, d.poster_time, out_dir)
    # Screencast only emits on repaint, so report the busiest half second.
    ts = [t for t, _ in frames]
    peak = max(sum(1 for u in ts if t <= u < t + 0.5) for t in ts) * 2
    print(f"{name}: {t1 - t0:.1f}s, peak {peak} fps", flush=True)


async def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("names", nargs="*", help="component names (default: all)")
    # Parallel recordings compete for the compositor and drop frames.
    parser.add_argument("-j", "--jobs", type=int, default=1)
    args = parser.parse_args()

    todo = [
        (path, s)
        for path, s in SPECS.items()
        if not args.names or path.split("/")[-1] in args.names or path in args.names
    ]
    sem = asyncio.Semaphore(args.jobs)
    async with async_playwright() as p:

        async def one(path: str, s: Spec):
            async with sem:
                try:
                    await record(p, path, s, COMPONENTS / path)
                except Exception as e:  # keep going; report at the end
                    print(f"{path}: FAILED {e!r}", flush=True)
                    return path

        failed = [f for f in await asyncio.gather(*(one(*t) for t in todo)) if f]
    if failed:
        sys.exit(f"failed: {', '.join(failed)}")


if __name__ == "__main__":
    asyncio.run(main())
