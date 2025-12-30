# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is the **Shiny for Python documentation website** - the official documentation, API reference, component gallery, and template showcase for the Shiny for Python framework. Built with Quarto, it combines hand-written conceptual documentation with auto-generated API reference docs extracted from the main py-shiny repository.

## Development Commands

### Initial Setup

```bash
# Clone and initialize submodules
git clone https://github.com/rstudio/pyshiny-site.git
cd pyshiny-site
make submodules

# Full build (creates venv, installs deps, generates API docs, builds site)
make all
```

### Common Development Workflow

```bash
# Serve site with live preview (watches for changes)
make serve

# Rebuild API documentation from py-shiny submodule
make quartodoc

# Rebuild component previews and Shinylive links
make components

# Build the complete website
make site

# Clean build artifacts
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

### Key Technologies

- **Quarto 1.7.23** - Static site generator and documentation platform
- **uv** - Fast Python package installer
- **Quartodoc** - API documentation generation from docstrings
- **Griffe** - Python code inspection
- **Shinylive 0.8.5** - WebAssembly-based Python runtime for browser-based examples
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

- **Quarto version:** Managed via qvm (Quarto Version Manager), pinned to 1.7.23
- **Python version:** 3.12 for development, 3.12 for CI
- **Shinylive version:** Pinned to 0.8.5 in requirements.txt
- **Package manager:** uv for fast Python package installation

## Troubleshooting

**If the build fails:**

1. Try cleaning: `make clean` or `make distclean`
2. Update submodules: `make submodules`
3. Reinstall dependencies: `make deps`
4. Check Quarto version: `quarto --version` (should be 1.7.23)

**If components aren't rendering:**

1. Regenerate components: `make components`
2. Check for syntax errors in component .qmd files
3. Verify Shinylive extension is installed

**If API docs are missing:**

1. Check py-shiny submodule is initialized: `ls py-shiny/`
2. Regenerate: `make quartodoc`
3. Check py-shiny/docs/Makefile for any errors
