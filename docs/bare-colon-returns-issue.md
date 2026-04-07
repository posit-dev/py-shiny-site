# Bare `:` in Returns Sections (Quarto 1.9 / Pandoc 3.8 Regression)

## Summary

After upgrading to Quarto 1.9.36, API reference pages show a bare `:` at the top of
their **Returns** sections. This affects 16 known pages across `api/core/` and
`api/express/`, and is an unintentional side effect of a Pandoc definition list parser
change in Pandoc 3.8 (which ships with Quarto 1.9).

**Before (Quarto 1.4 / Pandoc 3.4):**
> Returns
> A UI element.

**After (Quarto 1.9 / Pandoc 3.8):**
> Returns
> **:** A UI element.

## Affected Pages

16 pages identified in the audit:

**Core:** `reactive.invalidate_later`, `index`, `reactive.effect`,
`ui.update_text_area`, `ui.input_checkbox_group`, `ui.nav_control`,
`ui.input_radio_buttons`, `render.express`

**Express:** `express.ui.input_select`, `express.ui.update_tooltip`,
`express.ui.panel_title`, `express.render.image`, `express.ui.toolbar_input_select`,
`express.ui.navset_pill`, `express.ui.MarkdownStream`, `express.render.ui`

## Root Cause

### 1. Valid numpydoc convention in py-shiny docstrings

py-shiny uses `:` as the return "name" when a function has no meaningful return name
(the type is already declared in the signature). This is valid numpydoc style:

```python
def panel_title(title: str | Tag | TagList, ...) -> TagList:
    """
    Returns
    -------
    :
        A UI element.
    """
```

### 2. quartodoc generates empty definition list terms

quartodoc 0.11.1 with `table_style: description-list` renders these Returns entries as:

```markdown
## Returns {.doc-section .doc-section-returns}

<code>[]{.parameter-name} [:]{.parameter-annotation-sep} []{.parameter-annotation}</code>

:   A UI element.
```

The `<code>` line is a definition list **term** with empty name and annotation spans —
only the `[:]{.parameter-annotation-sep}` span has content.

### 3. Pandoc 3.8 tightened definition list parsing

Pandoc 3.8 (Quarto 1.9) rewrote definition list parsing to "behave like other lists"
with stricter conformance to the spec. Under Pandoc 3.4 (Quarto 1.4), the empty
`<code>` term was silently dropped and only the `dd` description rendered. Under
Pandoc 3.8, the term renders literally — producing the visible `:`.

This is **not** a deliberate change: there is no Quarto or Pandoc changelog entry
calling it out. It is an unintended consequence of the parser rewrite.

## Workarounds

### Option 1: Override `render(DocstringReturn)` in `_renderer.py` ✅ Recommended

The existing `render(DocstringParameter)` override in `_renderer.py` (line 150)
already conditionally omits the annotation separator when there is no annotation:

```python
@dispatch
def render(self, el: ds.DocstringParameter):
    param = f'<span class="parameter-name">{el.name}</span>'
    annotation = self.render_annotation(el.annotation)
    if annotation:  # ← only adds `:` when annotation exists
        param = f'{param}<span class="parameter-annotation-sep">:</span> ...'
    ...
```

The same pattern applied to `DocstringReturn` would suppress the empty term when
both `el.name` and `el.annotation` are absent — which is exactly the failing case.

**Tradeoffs:** requires a `make quartodoc` rebuild to regenerate `.qmd` files.
Surgical, consistent with the existing codebase style, forward-compatible.

### Option 2: CSS to hide empty `<dt>` elements

Add to `quarto-style.scss` or site CSS:

```css
.doc-section-returns dt:empty,
.doc-section-raises dt:empty {
  display: none;
}
```

The exact selector depends on how Pandoc 3.8 renders the empty term — requires
browser inspection to confirm. No `.qmd` rebuild needed.

**Tradeoffs:** brittle (depends on Pandoc's exact HTML output); hides symptoms
without fixing the source.

### Option 3: Switch `table_style` from `description-list` to `table`

Changing `table_style: table` in `_quartodoc-*.yml` switches quartodoc to emit
GitHub-flavored markdown tables instead of definition lists. Empty annotation cells
render as empty table cells rather than bare `:` terms.

**Tradeoffs:** significant visual regression — all Parameters and Returns sections
change appearance; existing CSS in `quarto-style.scss` targets `dt`/`dd` structure
and would need rewriting.

### Not viable: Disabling the `definition_lists` Pandoc extension

Setting `from: markdown-definition_lists` in `_quarto.yml` would prevent Pandoc from
interpreting `:   text` as a definition list, but it would also break all Parameters
sections sitewide since they rely on the same syntax.

## Recommendation

Implement Option 1 (`_renderer.py` override) as the near-term fix. Additionally,
file an upstream issue against [quartodoc](https://github.com/machow/quartodoc)
documenting the Pandoc 3.8 incompatibility — this affects any quartodoc user upgrading
to Quarto 1.9, not just py-shiny-site.
