---
name: testing-example-apps
description: Use when adding Playwright tests that verify a component's example apps under components/ actually run and behave — covers the shared components/conftest.py smoke_test fixture, create_example_fixture, per-component test_<name>.py layout, and py-shiny controller interaction tests. Reuses py-shiny's public testing API; no custom runner.
---

# Testing Example Apps

## Overview

Component example apps (`components/**/app.py`, `components/**/app-*.py`) are the source
of truth for each page — the shinylive links in `index.qmd` are generated from them. Smoke
coverage (it loads with no server, JS, or output errors) is centralized: a single
parametrized `components/test_examples_smoke.py` auto-discovers and smoke-tests every such app,
one `test_example_app_smoke[<relative path>]` case per app. This skill covers adding
[py-shiny Playwright](https://shiny.posit.co/py/docs/end-to-end-testing.html)
**interaction tests** for the primary Core + Express apps via py-shiny's controllers — you
do not write per-component smoke tests.

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
  - `example_app_paths()` / `launch_example_app()` — power the centralized smoke sweep below;
    you generally don't call these directly from a component's `test_<name>.py`.
- `components/test_examples_smoke.py` — smoke-tests EVERY discovered example app
  (`app.py` / `app-*.py`) as its own parametrized case; you do NOT write per-component
  smoke tests.
- `components/test_component_pages.py` — a static (non-browser) check that EVERY component
  page (`components/<section>/<name>/index.qmd`) ships at least one example app. A page
  with no `app.py` / `app-*.py` fails; opt a page out only by adding its `<section>/<name>`
  path to `NO_APP_ALLOWLIST` (with a reason). Runs under `make test-apps`.

## Steps to test a component

1. Create `components/<section>/<name>/test_<name>.py` next to the app files.
2. Smoke coverage is automatic — just make sure every example app is named `app.py` or
   `app-<name>.py` so it is discovered. Your `test_<name>.py` contains only interaction
   tests: drive the primary Core AND Express apps with `shiny.playwright.controller`:
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

`pytest.ini` sets `--browser chromium -n auto` as defaults, so you never pass them.

```bash
# Make targets (install deps + chromium, then run)
make test          # smoke sweep + per-component app tests
make test-smoke    # just the smoke sweep over every app
make test-apps     # just the per-component interaction + unit tests
make test-smoke PYTEST_ARGS='-k "layout/accordion"'          # narrow to one component
make test-smoke PYTEST_ARGS='--num-shards 6 --shard-id 0'    # one shard (CI does this)
```

Or drive pytest directly via `uv run` for fast local iteration (`uv run`
auto-discovers `.venv` — nothing to activate; chromium + xdist still apply from
`pytest.ini`; add `-n0` to run serially / one app at a time):

```bash
uv run pytest components/test_examples_smoke.py                      # whole smoke sweep
uv run pytest components/test_examples_smoke.py -k "layout/accordion"
uv run pytest components/layout/accordion/test_accordion.py          # one component's interaction tests
```

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
- Name every example app `app.py` or `app-<name>.py` — the smoke collector
  (`components/test_examples_smoke.py`) discovers apps by that convention; a differently named
  file is silently untested.
- Smoke coverage is automatic for every discovered `app.py`/`app-*.py`; per-component
  `test_<name>.py` files add interaction tests for the primary Core + Express apps.
