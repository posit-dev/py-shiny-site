---
name: testing-example-apps
description: Use when adding Playwright tests that verify a component's example apps under components/ actually run and behave — covers the shared components/conftest.py smoke_test fixture, create_example_fixture, per-component test_<name>.py layout, and py-shiny controller interaction tests. Reuses py-shiny's public testing API; no custom runner.
---

# Testing Example Apps

## Overview

Component example apps (`components/**/app-*.py`) are the source of truth for each
page — the shinylive links in `index.qmd` are generated from them. This skill adds
[py-shiny Playwright](https://shiny.posit.co/py/docs/end-to-end-testing.html) tests
that (1) **smoke-test** every `app-*.py` in a component dir (it loads with no server,
JS, or output errors) and (2) **interaction-test** the primary Core + Express apps via
py-shiny's controllers.

Everything uses the **public `shiny` package API** — `shiny.pytest.create_app_fixture`,
`shiny.playwright.controller`, `shiny.run.ShinyAppProc`. No custom test runner.

**Reference implementation:** `components/layout/accordion/test_accordion.py`.

## Shared infrastructure (already in place — do not re-create)

- `pytest.ini` (repo root): `testpaths = components` scopes pytest to the site's tests
  and away from the `py-shiny/` submodule.
- `components/conftest.py` provides:
  - `create_example_fixture(HERE / "app-NAME.py")` — returns a fixture yielding a running
    `ShinyAppProc`. Splits multi-file `## file:` shinylive apps into a temp dir; launches
    single-file apps directly.
  - `smoke_test` fixture — a callable `smoke_test(page, app, *, allow_stderr=(), allow_js=())`
    that navigates, waits for Shiny idle, and asserts no un-allow-listed server stderr,
    no JS console errors, and zero `.shiny-output-error`.

## Steps to test a component

1. Create `components/<section>/<name>/test_<name>.py` next to the app files.
2. **Smoke:** for every `app-*.py` in the dir, declare a module-level fixture and a test:
   ```python
   from pathlib import Path
   from playwright.sync_api import Page
   from conftest import create_example_fixture
   from shiny.run import ShinyAppProc

   HERE = Path(__file__).parent
   core_app = create_example_fixture(HERE / "app-core.py")

   def test_core_app_smoke(page: Page, core_app: ShinyAppProc, smoke_test) -> None:
       smoke_test(page, core_app)
   ```
   The module-level fixture variable name MUST match the test parameter name.
3. **Interaction:** drive the primary Core AND Express apps with `shiny.playwright.controller`:
   ```python
   from shiny.playwright import controller

   def test_core_interaction(page: Page, core_app: ShinyAppProc) -> None:
       page.goto(core_app.url)
       acc = controller.Accordion(page, "acc")
       acc.expect_open(["Section A"])
       acc.set(["Section B"])
       acc.expect_open(["Section B"])
   ```
   Find the controller for your component in `py-shiny/shiny/playwright/controller/`
   (e.g. `Accordion`, `InputSelect`, `OutputCode`, `Card`, `Sidebar`, ...).

## Value readouts: use `output_code`, not `output_text_verbatim`

Example apps that display a value (e.g. the currently open panels) should render it with
`ui.output_code(...)` / `@render.code` — the project's preferred verbatim output. Assert
on it with `controller.OutputCode(page, "<id>")`.

**Do NOT use `controller.OutputTextVerbatim` unless the component under test IS
`ui.output_text_verbatim`** (i.e. you are on the output-text-verbatim component page
itself). Using it elsewhere silently fails to match `output_code`'s `<pre>` and, worse,
encourages example apps to diverge (a bare Express `@render.text` renders a `<div>`, not a
`<pre>` — inconsistent with a Core `output_text_verbatim`). Standardize on `output_code`.

## Running

```bash
source .venv/bin/activate
pytest components/<section>/<name>/test_<name>.py --browser chromium
```
(chromium is already installed via `playwright install`.)

## Rules

- Test the **raw `app-*.py`** files, never the shinylive URLs (they are derived). After
  editing any `app-*.py`, regenerate the page's shinylive links
  (`make components-shinylive-links FILES="components/<section>/<name>/index.qmd"`) and
  commit the updated `index.qmd`, or `check-shinylive-links` CI fails.
- Display values with `output_code` / `@render.code`; only use `controller.OutputTextVerbatim`
  when the component under test is itself `output_text_verbatim`.
- In Core apps, pair matching output/render names: `ui.output_code("id")` ↔ `@render.code`
  named `id` (never `ui.output_code` + `@render.text`). Every `ui.output_<X>` has a
  same-named `@render.<X>`.
- Known-benign warnings: pass them per test via `smoke_test(..., allow_stderr=[...])` —
  do NOT broaden the global default in `conftest.py`.
- **Never** add `*.py` to `_quarto.yml` `resources:` — `.py` files are already excluded
  from `_build/`.
- Every non-Preview app should get both a smoke test; interaction tests cover the primary
  Core + Express apps at minimum.
