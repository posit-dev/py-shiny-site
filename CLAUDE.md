# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is the **Shiny for Python documentation website** - the official documentation, API reference, component gallery, and template showcase for the Shiny for Python framework. Built with Quarto, it combines hand-written conceptual documentation with auto-generated API reference docs extracted from the main py-shiny repository.

## Development Commands

### Initial Setup

```bash
# Clone and initialize submodules
git clone https://github.com/posit-dev/py-shiny-site.git
cd py-shiny-site
make submodules

# Full build (creates venv, installs deps, generates API docs, builds site)
make all
```

Or, for any fresh checkout or git worktree, one command does submodules + deps
+ generated docs and seeds `_build/`/render caches from a sibling checkout:

```bash
make ai-setup
```

(Conductor workspaces run this automatically via `.conductor/settings.toml`.)

### Common Development Workflow

```bash
# One-command init for a fresh checkout/worktree (submodules, deps, generated
# docs; seeds _build/ and render caches from a sibling checkout when possible)
make ai-setup

# Serve with live preview. Runs a parallel full build first ONLY if _build/ is
# missing or older than _quarto.yml; otherwise starts instantly and re-renders
# just the pages you edit.
make serve

# Serve with a full SERIAL initial render (~35 min). Use after changing
# _quarto.yml, the SCSS theme, includes, or extensions — `make serve` skips
# the up-front full render, so site-wide config changes won't propagate there.
make serve-serial

# Full site build using local parallel shards (~9 min on a multi-core machine)
make site-parallel

# Full serial site build (the fidelity reference; what CI shards run internally)
make site

# Rebuild API documentation from py-shiny submodule
# (skips itself when the submodule commit, _renderer.py, quartodoc configs,
# and requirements.txt are unchanged — stamp file: .quartodoc-stamp)
make quartodoc

# Rebuild component previews and Shinylive links
make components

# Clean build artifacts (also purges .quarto/shinylive-cache)
make clean

# Pull latest changes including submodules
git pull
make submodules
make all
```

### Individual Build Steps

When iterating, run steps separately for efficiency:

```bash
# Install/update Python dependencies
make deps

# Generate API docs (outputs to api/)
make quartodoc

# Update component Shinylive links
make components-shinylive-links

# Generate static component previews
make components-static
```

### Virtual Environment

The Makefile automatically creates a venv using `uv`. To run commands manually in the same environment:

```bash
source .venv/bin/activate  # Activate venv
# ... run commands ...
deactivate                  # Exit venv
```

### Cleaning

```bash
make clean              # Remove build files
make clean-extensions   # Remove Quarto extensions
make clean-venv         # Remove virtual environment
make distclean          # Remove everything (clean + extensions + venv)
```

## Architecture

### Directory Structure

- **docs/** - Conceptual documentation (reactivity, UI patterns, modules, testing, GenAI integration)
- **components/** - Interactive component library with live examples (inputs, outputs, display messages)
- **api/** - Auto-generated API reference
  - `api/express/` - Shiny Express API
  - `api/core/` - Shiny Core API
  - `api/testing/` - Testing API
- **templates/** - Starter app templates (dashboards, chatbots, AI apps)
- **gallery/** - Example application showcase
- **get-started/** - Tutorial and getting started guides
- **layouts/** - Layout pattern documentation
- **py-shiny/** - Git submodule pointing to main py-shiny repository
- **_extensions/** - Quarto extensions (shinylive, interlinks, quartodoc)
- **scripts/** - Build and post-render scripts

### Build Pipeline

The build follows this sequence:

1. **Submodules** - Update py-shiny submodule to specific commit
2. **Dependencies** - Install Python packages via uv
3. **Quartodoc** - Generate API docs from py-shiny source code
4. **Components** - Generate static previews & update Shinylive links
5. **Quarto** - Render all .qmd files to HTML
6. **Post-render** - Run post-processing scripts

### Sharded (parallel) rendering

Full renders are split into weight-balanced slices and merged:

- `scripts/ci-shard.py --shard K --count N` rewrites `_quarto.yml`'s
  `project.render` to slice K **and** transforms sidebar configs (bare qmd
  paths → `text`/`href` entries, titles from front matter/H1) so Quarto
  doesn't prune navigation to the shard; listing pages are co-sharded with
  their globbed items. Must run AFTER `make quartodoc` (it also transforms
  the generated `api/*/_sidebar.yml` files). `--count 1` is a no-op.
- `scripts/ci-merge.py --shards DIR --out _build` overlays shard outputs,
  concatenates the shard-scoped `search.json`/`llms.txt`, keeps the real
  homepage over per-shard redirect stubs, and rewrites residual cross-shard
  `.qmd` hrefs to `.html`.
- CI runs 10 shard jobs + a merge/deploy job; `make site-parallel` does the
  same locally in APFS clone-copy scratch trees (`SHARDS=6` default).
- Known cosmetic gap: navbar section-highlight is missing on ~38 pages whose
  navbar target renders in another shard.
- Latent constraint: the listing co-sharding merge is not fully transitive —
  revisit `ci-shard.py` before adding a second qmd-glob listing page.

### Key Technologies

- **Quarto 1.9.36** - Static site generator and documentation platform
- **uv** - Fast Python package installer
- **Quartodoc** - API documentation generation from docstrings
- **Griffe** - Python code inspection
- **Shinylive** (version pinned in requirements.txt) - WebAssembly-based Python runtime for browser-based examples
- **Python 3.12** - Development environment (CI uses 3.12)

### Custom Documentation Renderer

The `_renderer.py` file implements a custom Quartodoc renderer that:

- Extracts examples from py-shiny source code (`shiny/examples/{name}/`)
- Converts them to Shinylive interactive demos
- Handles multi-file examples with syntax highlighting
- Supports binary files via base64 encoding
- Applies HTML escaping and link formatting

Example directories are discovered automatically: if `shiny/examples/{function_name}/app.py` exists, it's embedded as an interactive example in the API docs.

### Quarto Extensions

The site uses four key Quarto extensions (in `_extensions/`):

1. **shinylive** - Embeds interactive Python examples that run in the browser
2. **interlinks** - Cross-references to external docs (Python, matplotlib, etc.)
3. **line-highlight** - Enhanced syntax highlighting
4. **quartodoc** - API documentation generation

Update extensions with:
```bash
make clean-extensions quarto-extensions
```

**Note:** the shinylive extension carries a local performance patch
(`scripts/patches/shinylive-cache.patch`) that memoizes its subprocess calls to
`.quarto/shinylive-cache/`. `make quarto-extensions` re-applies it after
re-downloading the extension and fails loudly if upstream drift breaks it — see
the patch file's header for how to re-port or retire it. If you edit the cache
block in `_extensions/quarto-ext/shinylive/shinylive.lua`, regenerate the patch
file so the two stay in sync (`git apply --reverse --check` must pass).

### Git Submodule Pattern

This repository uses `py-shiny/` as a git submodule. This allows:

- API docs stay in sync with framework code
- Documentation can reference specific py-shiny commits
- Source code examples are extracted directly from py-shiny

**Important submodule notes:**

- By default, submodules are in detached HEAD state
- `make submodules` updates to the commit referenced by this repo
- `make submodules-pull` pulls latest commits (use carefully)
- When updating submodule reference, commit the change to this repo

### Content Architecture

**Content types:**

1. **Hand-written guides** (.qmd files in docs/, get-started/) - Conceptual documentation
2. **Component pages** (components/) - Each component has its own directory with examples
3. **API reference** (api/) - Auto-generated from py-shiny docstrings
4. **Templates** (templates/) - Starter templates with code and screenshots
5. **Gallery** (gallery/) - Showcase applications

**Interactive examples:**

All code examples use Shinylive to run Python in the browser via WebAssembly. This means examples are immediately runnable without a backend server.

## Configuration Files

- **_quarto.yml** - Main Quarto configuration (website structure, navigation, sidebars)
- **Makefile** - Build system orchestration
- **requirements.txt** - Python dependencies for building the site
- **_renderer.py** - Custom Quartodoc renderer for Shiny-specific formatting
- **scripts/post-render.py** - Post-processing after Quarto render

## Deployment

- **Production:** Commits to `main` branch trigger automatic build and deploy via GitHub Actions
- **Preview:** Pull requests generate preview deployments (e.g., `pr-123--pyshiny.netlify.app`)
- **Pipeline:** 10 parallel shard jobs render slices of the site, then a `deploy` job merges the artifacts (`scripts/ci-merge.py`) and publishes — ~9 min end to end. A failed shard skips the deploy entirely. Superseded runs are cancelled by a concurrency group (only the newest commit per ref deploys).
- **Escape hatch:** run the workflow manually (`workflow_dispatch`) with `full_render = true` for a single unsharded build job.
- **CI caches:** `.quarto/shinylive-cache/` persists across runs via `actions/cache` (content-addressed keys; safe to restore stale).
- **Platform:** Hosted on Netlify
- **Output directory:** `_build/` (configured in _quarto.yml)

## Working with Components

Component pages follow a consistent structure:

1. Component description and usage
2. Live Shinylive examples
3. Variations and options
4. Related components

To update component examples:

```bash
# Regenerate Shinylive links
make components-shinylive-links

# Regenerate static preview images
make components-static
```

## Working with API Documentation

API docs are generated from the py-shiny repository:

1. Update py-shiny submodule if needed: `make submodules-pull`
2. Regenerate docs: `make quartodoc`
3. Docs appear in `api/express/`, `api/core/`, `api/testing/`

The custom renderer automatically extracts examples from `py-shiny/shiny/examples/{function_name}/` and embeds them as interactive Shinylive demos.

## Dependencies and Version Management

- **Quarto version:** Managed via qvm (Quarto Version Manager), pinned to 1.9.36
- **Python version:** 3.12 for development, 3.12 for CI
- **Shinylive version:** Pinned in requirements.txt (bumping it invalidates `.quarto/shinylive-cache/`, whose keys include the requirements.txt hash)
- **Package manager:** uv for fast Python package installation

## Site Quality Checks

**`make compare-versions`** — viewport comparison between production and a local build using Playwright + Claude vision via AWS Bedrock. Run it before merging any change that could affect rendered output site-wide: Quarto version upgrades, Shinylive version upgrades, `_quarto.yml` structural changes, `_renderer.py` changes, or other dependency upgrades. Writes a timestamped markdown report to `tests/`; start with the executive summary.

### How to run

```bash
# Serve the local build first (serves on localhost:1414 by default;
# make sure _build/ is a current full build — run `make site-parallel` first)
make serve

# In another terminal
make compare-versions
```

Narrow scope with `FILTER` or `EXCLUDE`:

```bash
make compare-versions FILTER=docs/
make compare-versions FILTER=api/core/
make compare-versions EXCLUDE=api/
```

Override the URLs if needed:

```bash
make compare-versions COMPARE_OLD_URL=https://shiny.posit.co/py COMPARE_NEW_URL=http://localhost:1414
```

The report is written to `tests/compare-versions-<timestamp>.md`. The executive summary at the top groups findings by priority — start there.

## Troubleshooting

**If the build fails:**

1. Try cleaning: `make clean` or `make distclean`
2. Update submodules: `make submodules`
3. Reinstall dependencies: `make deps`
4. Check Quarto version: `quarto --version` (should be 1.9.36)

**If components aren't rendering:**

1. Regenerate components: `make components`
2. Check for syntax errors in component .qmd files
3. Verify Shinylive extension is installed

**If API docs are missing or stale:**

1. Check py-shiny submodule is initialized: `ls py-shiny/`
2. Regenerate: `make quartodoc` (if it says "up to date" but you believe otherwise, `rm .quartodoc-stamp` and re-run)
3. Check py-shiny/docs/Makefile for any errors

**If `make serve` shows stale content site-wide:**

`make serve` intentionally skips the initial full render. After config/theme/extension changes, use `make serve-serial`, or rebuild with `make site-parallel` first.
