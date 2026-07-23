This repository contains the sources for the [Shiny for Python](https://shiny.posit.co/py/) web site.

## Quick start for contributors

```bash
git clone https://github.com/posit-dev/py-shiny-site.git
cd py-shiny-site
make ai-setup   # submodules, Python deps, generated API docs, component previews
make serve      # live preview at http://localhost:1414
```

`make ai-setup` is a one-command initialization for any fresh checkout or git
worktree. It also seeds heavy gitignored artifacts (`_build/`, render caches)
from a sibling checkout when one exists — on a machine that already has a
built copy of the site, a new worktree is ready in seconds. Prerequisites it
doesn't install for you:

- [**uv**](https://docs.astral.sh/uv/getting-started/installation/) — the
  Python package/venv manager. `make` runs every Python tool through it; if uv
  isn't on your `PATH`, `make` stops immediately with the install link above.
- [**Homebrew**](https://brew.sh) — used to install
  [qvm](https://github.com/dpastoor/qvm), which pins the Quarto version.
- `git`.

The Python venv and Quarto itself are still installed by `make` on demand.

Running `make` by itself lists all targets.

## Everyday development

| Command | What it does |
|---|---|
| `make serve` | Live preview. If `_build/` is missing it first runs a **parallel** full build (~7–10 min); after that, startup is instant and only pages you edit are re-rendered. |
| `make serve-serial` | Live preview with a full **serial** initial render (~35 min). Use this after changing `_quarto.yml`, the SCSS theme, includes, or extensions — `make serve` intentionally skips the up-front full render, so site-wide config changes won't propagate to unedited pages there. |
| `make site-parallel` | Full site build into `_build/` using local parallel shards (`SHARDS=6` by default). The honest full rebuild, several times faster than `make site` on multi-core machines. |
| `make site` | Full serial site build (what CI's shards run under the hood; the reference for fidelity). |
| `make quartodoc` | Regenerate API reference qmds from the py-shiny submodule. Skips itself when nothing relevant changed (submodule commit, `_renderer.py`, quartodoc configs, `requirements.txt`). |
| `make components` | Rebuild component static previews and Shinylive links. |
| `make clean` | Remove build outputs and render caches. |

### How builds got fast (and what that means for you)

- The vendored shinylive Quarto extension is patched to memoize its subprocess
  calls in `.quarto/shinylive-cache/` (see the note in `CLAUDE.md` and
  `scripts/patches/shinylive-cache.patch`). **If you edit
  `_extensions/quarto-ext/shinylive/shinylive.lua`, regenerate the patch file**
  so `make quarto-extensions` can re-apply it after extension upgrades.
- `scripts/ci-shard.py` / `scripts/ci-merge.py` split a full render into
  balanced slices and merge the outputs; both CI and `make site-parallel` use
  them. Known cosmetic limitation: the navbar section-highlight is missing on
  a few dozen pages in sharded builds.

## Working in the virtualenv

`make` runs everything through `uv` inside a uv-managed virtualenv at `.venv/`.
To run commands in it yourself, prefix them with `uv run` — it auto-discovers
`.venv`, so there's nothing to activate:

```bash
uv run python -c "import shiny; print(shiny.__version__)"
uv run pytest components/layout/accordion/test_accordion.py
```

## Testing example apps

Every example app under `components/` is exercised by Playwright tests
(reusing py-shiny's public testing API — no custom runner):

```bash
make test          # smoke sweep (every app-*.py) + per-component interaction tests
make test-smoke    # just the smoke sweep
make test-apps     # just the per-component interaction/unit tests
```

`pytest.ini` defaults to the chromium browser and xdist (`-n auto`); narrow a
run with `PYTEST_ARGS`, e.g. `make test-smoke PYTEST_ARGS='-k "layout/accordion"'`.
See the `testing-example-apps` skill for how to add tests for a component.

## Pulling changes

```bash
git pull
make submodules   # sync py-shiny submodule to the referenced commit
make all          # quartodoc + components + site
```

If something looks stale, `make clean` (or `make distclean` to also remove
extensions and the venv) and rebuild.

Note: submodules check out a specific commit in detached-HEAD mode. If you
develop inside `py-shiny/`, check out a branch there and keep it in sync with
the commit this repo references.

## Updating Quarto extensions

Extensions are checked into `_extensions/` so no install step is needed. To
update them:

```bash
make clean-extensions quarto-extensions
```

then commit the result. This re-downloads the extensions and re-applies the
local shinylive cache patch — it fails loudly if upstream changed in a way
that breaks the patch (see `scripts/patches/shinylive-cache.patch` for how to
re-port or retire it).

## CI and deployment

- Every push to a PR builds the site on GitHub Actions: six parallel shard
  jobs render slices of the site, then a deploy job merges them and publishes
  a preview to Netlify (`pr-<N>--pyshiny.netlify.app`, ~12 minutes end to
  end). Superseded runs are cancelled automatically.
- Commits to `main` deploy to production the same way.
- Escape hatch: run the workflow manually (`workflow_dispatch`) with
  `full_render = true` to build in a single unsharded job.
- A separate **`check-shinylive-links`** workflow runs on every PR: it
  regenerates the component Shinylive links and fails if the committed links
  are out of date. So after editing any `app-*.py`, run
  `make components-shinylive-links` (optionally scoped with `FILES="..."`) and
  commit the updated `index.qmd`.
- **`test-smoke`** (sharded, 6 jobs) and **`test-apps`** run the example-app
  Playwright tests on every PR (`make test-smoke` / `make test-apps`). They use
  a cached Docker Playwright browser, so no per-job browser download.
- Shared workflow setup lives in local composite actions under
  `.github/internal/` (`setup-uv`, `setup-py-shiny-site`,
  `setup-playwright-remote`).

## Site quality checks

`make compare-versions` runs a viewport comparison between production and a
local build (Playwright + vision model). Run it before merging changes that
could affect rendered output site-wide. See `CLAUDE.md` for details and
filtering options.
