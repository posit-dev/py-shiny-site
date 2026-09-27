"""Regression tests for the Shinylive service-worker reload loop.

Shinylive's ``load-shinylive-sw.js`` ends with

    navigator.serviceWorker.ready.then(() => {
      navigator.serviceWorker.controller || window.location.reload();
    });

``ready`` resolves once the worker is *active*, which is before it has claimed
the page, so the check fails and the page reloads: Chrome discards a fully
loaded components page and starts over on every first visit.
``include-in-header.html`` holds ``ready`` until the page is actually
controlled, so the reload never fires, and caps it at one reload per tab if
control never arrives.

The patch is site-wide, but the components list page is where the wasted reload
hurts most (43 previews reloaded from scratch), so these tests live alongside
the other component-preview tests.
"""

from __future__ import annotations

import functools
import http.server
import socketserver
import threading
from collections import Counter
from pathlib import Path
from typing import Iterator

import pytest
from playwright.sync_api import Page

REPO_ROOT = Path(__file__).parent.parent
INCLUDE_IN_HEADER = REPO_ROOT / "include-in-header.html"

# Mimics the tail of Shinylive's loader: register the worker, then reload the
# page unless it is already controlled.
SHINYLIVE_LOADER = """
navigator.serviceWorker.register(
  new URLSearchParams(location.search).get("sw") + ".js"
);
navigator.serviceWorker.ready.then(() => {
  navigator.serviceWorker.controller || window.location.reload();
});
"""

CLAIMING_WORKER = """
self.addEventListener("install", (e) => e.waitUntil(self.skipWaiting()));
self.addEventListener("activate", (e) => e.waitUntil(self.clients.claim()));
"""

# A worker that activates but never claims: the shape that traps Firefox.
IDLE_WORKER = """
self.addEventListener("install", (e) => e.waitUntil(self.skipWaiting()));
"""


def service_worker_patch() -> str:
    """The `navigator.serviceWorker.ready` patch, as shipped in the site header."""
    blocks = INCLUDE_IN_HEADER.read_text().split("</script>")
    patch = next(b for b in blocks if "shinylive-sw-reloaded" in b)
    return patch.split("<script>", 1)[1]


@pytest.fixture
def site(tmp_path: Path) -> Iterator[tuple[str, Counter]]:
    """Serve a page that registers a service worker; count how often it loads."""
    (tmp_path / "claim.js").write_text(CLAIMING_WORKER)
    (tmp_path / "idle.js").write_text(IDLE_WORKER)
    (tmp_path / "index.html").write_text(
        "<!doctype html><title>sw test</title>"
        f"<script>{service_worker_patch()}</script>"
        f"<script>{SHINYLIVE_LOADER}</script>"
    )

    requests: Counter = Counter()

    class Handler(http.server.SimpleHTTPRequestHandler):
        protocol_version = "HTTP/1.1"

        def do_GET(self) -> None:
            requests[self.path.split("?")[0]] += 1
            super().do_GET()

        def log_message(self, format: str, *args: object) -> None:
            pass

    class Server(socketserver.ThreadingTCPServer):
        allow_reuse_address = True
        daemon_threads = True

    server = Server(
        ("127.0.0.1", 0), functools.partial(Handler, directory=str(tmp_path))
    )
    threading.Thread(target=server.serve_forever, daemon=True).start()
    try:
        yield f"http://127.0.0.1:{server.server_address[1]}/", requests
    finally:
        server.shutdown()
        server.server_close()


def test_page_does_not_reload_once_the_worker_claims_it(
    page: Page, site: tuple[str, Counter]
) -> None:
    base, requests = site
    page.goto(f"{base}?sw=claim")
    page.wait_for_timeout(4000)

    assert requests["/"] == 1
    assert page.evaluate("!!navigator.serviceWorker.controller")


def test_a_worker_that_never_claims_cannot_loop_the_page(
    page: Page, site: tuple[str, Counter]
) -> None:
    base, requests = site
    page.goto(f"{base}?sw=idle")
    page.wait_for_timeout(6000)

    # Shinylive's recovery reload still gets one chance; the patch stops it
    # from repeating, which is what turned this into an endless loop.
    assert requests["/"] <= 2
