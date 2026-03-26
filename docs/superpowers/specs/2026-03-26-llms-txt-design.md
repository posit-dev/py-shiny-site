# Design: Add llms.txt and llms-full.txt

**Issue:** https://github.com/posit-dev/py-shiny-site/issues/363
**Date:** 2026-03-26

## Overview

Add `llms.txt` and `llms-full.txt` to the Shiny for Python documentation site, following the [llmstxt.org](https://llmstxt.org/) specification. These files help LLMs discover and consume the site's documentation. A generation script keeps them in sync with the source content, and a CI check ensures they stay up to date.

## File Formats

### llms.txt

A concise overview with links, following the llmstxt.org spec:

- **H1 heading:** `# Shiny for Python`
- **Blockquote:** Brief summary of the framework
- **H2 sections** matching the site's navigation structure, each containing a list of links
- Links use page titles only (no descriptions): `- [Page Title](url)`
- Base URL: `https://shiny.posit.co/py/`

Example:

```markdown
# Shiny for Python

> Shiny for Python is a framework for building reactive web applications and dashboards in pure Python. It features a reactive execution engine, built-in UI components, and support for generative AI integration.

## Get Started

- [Get Started](https://shiny.posit.co/py/get-started/)
- [What is Shiny?](https://shiny.posit.co/py/get-started/what-is-shiny.html)
- [Install](https://shiny.posit.co/py/get-started/install.html)
...

## Concepts

- [Overview](https://shiny.posit.co/py/docs/overview.html)
...

## Components

### Inputs
- [Action Button](https://shiny.posit.co/py/components/inputs/action-button/)
...

### Outputs
- [Data Grid](https://shiny.posit.co/py/components/outputs/data-grid/)
...

## API Reference

### Shiny Express
- [Shiny Express API](https://shiny.posit.co/py/api/express/)

### Shiny Core
- [Shiny Core API](https://shiny.posit.co/py/api/core/)

### Testing
- [Testing API](https://shiny.posit.co/py/api/testing/)

## Templates
- [Dashboard Tips](https://shiny.posit.co/py/templates/dashboard-tips/)
...
```

### llms-full.txt

Same H1 and blockquote header, but with full cleaned page content inlined:

- **H2** per site section
- **H3** per page (using page title)
- Full cleaned content under each H3
- `---` separator between pages

Example:

```markdown
# Shiny for Python

> Shiny for Python is a framework for building reactive web applications...

## Get Started

### What is Shiny?

[full cleaned content of what-is-shiny.qmd]

---

### Install

[full cleaned content of install.qmd]

---
```

## Content Scope

**Included sections:**
- Get Started (`get-started/`)
- Concepts (`docs/`)
- Components — inputs, outputs, display messages (`components/`) — including example code
- Layouts (`layouts/`)
- API Reference (`api/express/`, `api/core/`, `api/testing/`)
- Templates (`templates/`) — including code

**Excluded:**
- Gallery (`gallery/`)

## Generation Script

**File:** `scripts/generate-llms-txt.py`

**Inputs:**
- `_quarto.yml` — site structure, section ordering, page list
- `.qmd` files referenced in the config
- Hardcoded site description (the blockquote summary)
- Base URL constant: `https://shiny.posit.co/py/`

**Processing:**

1. Parse `_quarto.yml` to extract navbar and sidebar structures
2. Walk the structure to build an ordered list of sections and pages
3. For each page, read the `.qmd` file:
   - Extract `title` (or `pagetitle`) from YAML frontmatter
   - For `llms-full.txt`: clean the content (see cleaning rules below)
4. Write `llms.txt` to repo root
5. Write `llms-full.txt` to repo root

**Determinism requirement:** Output is a pure function of the input files. No timestamps, no randomness. If only `page1.qmd` changes, only page1's section in the output changes. Summary portions (H1, blockquote) are regenerated each time from the hardcoded constant.

### QMD Cleaning Rules (for llms-full.txt)

- Remove YAML frontmatter (`---`...`---` block at start of file)
- Remove Quarto div fences (lines matching `:::+\s*\{.*\}` and bare `:::+`)
- Remove raw HTML blocks (` ```{=html} ` through closing ` ``` `)
- Remove inline HTML tags (`<div>`, `<span>`, `<style>`, etc.)
- Convert Quarto code block syntax to standard markdown (` ```{python} ` becomes ` ```python `)
- Preserve: markdown headings, prose text, lists, fenced code blocks, links
- Collapse runs of 3+ blank lines down to 2

## Build Integration

### Makefile

New target with dependency on `quartodoc` (so API docs are available):

```makefile
## Generate llms.txt and llms-full.txt
.PHONY: llms-txt
llms-txt: $(PYBIN) quartodoc
	. $(PYBIN)/activate && python scripts/generate-llms-txt.py
```

Update `all` target:

```makefile
all: quartodoc components llms-txt site
```

### Quarto Resources

Add to `_quarto.yml` `project.resources` so files are copied to `_build/`:

```yaml
resources:
  - /llms.txt
  - /llms-full.txt
```

### CI Check

Add a step to `.github/workflows/deploy-docs.yml` after the build step:

```yaml
- name: Verify llms.txt is up to date
  run: |
    make llms-txt
    if ! git diff --exit-code llms.txt llms-full.txt; then
      echo ""
      echo "ERROR: llms.txt or llms-full.txt is out of date."
      echo "Run 'make llms-txt' locally and commit the updated files."
      exit 1
    fi
```

## File Locations

| File | Location | Committed? |
|---|---|---|
| `llms.txt` | repo root | Yes |
| `llms-full.txt` | repo root | Yes |
| `scripts/generate-llms-txt.py` | `scripts/` | Yes |

## Workflow

**Adding/changing a docs page:**
1. Edit `.qmd` files as usual
2. Run `make llms-txt`
3. Commit the updated `llms.txt` and `llms-full.txt` alongside the content changes
4. CI verifies they're in sync; fails with instructions if not

**Updating the py-shiny submodule:**
1. Update submodule (`make submodules-pull`, commit new ref)
2. Run `make llms-txt` (which runs `quartodoc` first)
3. Commit updated files

## API Docs Handling

The API docs (`api/express/`, `api/core/`, `api/testing/`) are generated from the py-shiny submodule via `make quartodoc`. They don't exist in a fresh checkout.

- `llms.txt`: API links are always included (they're known, fixed URLs)
- `llms-full.txt`: API content is included because `llms-txt` depends on `quartodoc` in the Makefile, ensuring the files are always present when the script runs
