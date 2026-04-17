"""Generate llms-full.txt from site source files."""

import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator

BASE_URL = "https://shiny.posit.co/py/"

SITE_DESCRIPTION = (
    "Shiny for Python is a framework for building reactive web applications "
    "and dashboards in pure Python. It features a reactive execution engine, "
    "built-in UI components, and support for generative AI integration."
)


_HTML_ELEMENTS = frozenset(
    "a abbr address area article aside audio b base bdi bdo blockquote body br "
    "button canvas caption cite code col colgroup data datalist dd del details "
    "dfn dialog div dl dt em embed fieldset figcaption figure footer form h1 h2 "
    "h3 h4 h5 h6 head header hr html i iframe img input ins kbd label legend li "
    "link main map mark menu meta meter nav noscript object ol optgroup option "
    "output p picture pre progress q rp rt ruby s samp script section select "
    "small source span strong style sub summary sup table tbody td template "
    "textarea tfoot th thead time tr track u ul var video wbr "
    "svg path circle rect line polyline polygon ellipse g defs use text tspan "
    "dotlottie slot".split()
)


def _strip_html_tag(m: re.Match) -> str:
    """Return empty string for real HTML tags; preserve angle-bracket placeholders."""
    inner = m.group(1).strip()
    # Closing tag: </foo>
    if inner.startswith("/"):
        return ""
    # Tag with attributes or self-closing slash
    if " " in inner or "=" in inner or inner.endswith("/"):
        return ""
    # Simple bare tag — only strip if it's a known HTML element
    tag_name = inner.lower()
    return "" if tag_name in _HTML_ELEMENTS else m.group(0)


def _strip_html_outside_code(line: str) -> str:
    """Strip HTML tags from a line, preserving backtick spans and placeholders."""
    parts = re.split(r"(`[^`]*`)", line)
    return "".join(
        part if i % 2 == 1 else re.sub(r"<([^>]+)>", _strip_html_tag, part)
        for i, part in enumerate(parts)
    )


def _resolve_links(content: str, file_path: str) -> str:
    """Rewrite relative/qmd links in content to absolute URLs."""
    page_dir = Path(file_path).parent

    def replace(m: re.Match) -> str:
        text, href = m.group(1), m.group(2)
        if href.startswith(("http://", "https://", "#", "mailto:")):
            return m.group(0)
        bare = href.split("#")[0]
        if not bare:
            return m.group(0)
        if bare.startswith("/"):
            resolved = bare.lstrip("/")
        else:
            resolved = os.path.normpath(str(page_dir / bare))
        return f"[{text}]({file_path_to_url(resolved)})"

    return re.sub(r"\[([^\]]+)\]\(([^)]+)\)", replace, content)


_TEMPLATE_HEADINGS = re.compile(
    r"^#{1,3} (Details|Variations|Relevant Functions)$"
)


def clean_qmd_content(content: str, file_path: str = "") -> str:
    """Strip Quarto-specific markup from .qmd content, keeping prose and code."""
    lines = content.split("\n")
    result_lines: list[str] = []
    in_frontmatter = False
    in_raw_html_block = False
    in_html_comment = False
    in_code_block = False
    code_block_buf: list[str] = []
    code_block_hidden = False
    frontmatter_count = 0

    for line in lines:
        stripped = line.strip()

        # Handle YAML frontmatter (first --- ... --- block)
        if stripped == "---" and frontmatter_count < 2:
            frontmatter_count += 1
            in_frontmatter = not in_frontmatter
            continue
        if in_frontmatter:
            continue

        # Handle raw HTML blocks: ```{=html} ... ```
        if stripped.startswith("```{=html}"):
            in_raw_html_block = True
            continue
        if in_raw_html_block:
            if stripped == "```":
                in_raw_html_block = False
            continue

        # Handle multi-line HTML comments: <!-- ... -->
        if in_html_comment:
            if "-->" in line:
                in_html_comment = False
            continue
        if "<!--" in stripped:
            if "-->" not in line[line.index("<!--"):]:
                in_html_comment = True
                continue
            line = re.sub(r"<!--.*?-->", "", line).rstrip()
            stripped = line.strip()
            if not stripped:
                continue

        # Handle code blocks: buffer content, drop if hidden (echo/include: false)
        if in_code_block:
            if stripped == "```":
                in_code_block = False
                if not code_block_hidden:
                    result_lines.extend(code_block_buf)
                    result_lines.append(line)
                code_block_buf = []
                code_block_hidden = False
            else:
                if re.match(r"^#\|\s*(echo|include):\s*false", stripped):
                    code_block_hidden = True
                elif not re.match(r"^#\|", stripped):
                    code_block_buf.append(line)
            continue

        # Skip Quarto div fences: :::{.class}, ::: callout-note, ::::, bare :::
        if re.match(r"^:{3,}", stripped):
            continue

        # Strip component template headings (authoring artifacts, not content)
        if _TEMPLATE_HEADINGS.match(stripped):
            continue

        # Code block opener — convert Quarto/shinylive syntax, start buffering
        if stripped.startswith("```"):
            in_code_block = True
            code_block_hidden = False
            code_block_buf = []
            m = re.match(r"^```\s*\{(shinylive-)?(\w+)\}", stripped)
            if m:
                code_block_buf.append(f"```{m.group(2)}")
            else:
                code_block_buf.append(line)
            continue

        # Remove inline HTML tags (but not inside backtick spans)
        line = _strip_html_outside_code(line)

        # Skip lines that became empty after HTML removal (were pure HTML),
        # and skip "Show code" / "Hide code" fold labels (may be wrapped in HTML)
        stripped_after = line.strip()
        if stripped_after in ("Show code", "Hide code"):
            continue
        if not stripped_after and stripped:
            continue

        result_lines.append(line)

    # Collapse 3+ consecutive blank lines to 2
    text = "\n".join(result_lines)
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = text.strip() + "\n"

    if file_path:
        text = _resolve_links(text, file_path)

    return text


def clean_section_name(raw: str) -> str:
    """Strip Quarto markup from sidebar section names."""
    # Remove ![...](...)  with optional {...} attributes
    result = re.sub(r"!\[.*?\]\(.*?\)(\{.*?\})?", "", raw)
    # Remove entire <span>...</span> blocks (including content)
    result = re.sub(r"<span[^>]*>.*?</span>", "", result, flags=re.DOTALL)
    # Remove remaining HTML tags (open/close)
    result = re.sub(r"<[^>]+>", "", result)
    # Extract text from __text__ bold markers
    result = re.sub(r"__(.+?)__", r"\1", result)
    # Remove {.class} attributes
    result = re.sub(r"\{[^}]*\}", "", result)
    return result.strip()


def extract_title(content: str) -> "str | None":
    """Extract title from .qmd YAML frontmatter.

    Returns pagetitle if present (takes precedence), else title, else None.
    Uses regex parsing since PyYAML may not be available.
    """
    # Find the frontmatter block
    match = re.match(r"^---\s*\n(.*?)\n---\s*\n", content, re.DOTALL)
    if not match:
        return None
    frontmatter = match.group(1)

    # Try PyYAML first if available
    try:
        import yaml  # type: ignore

        data = yaml.safe_load(frontmatter)
        if isinstance(data, dict):
            if "pagetitle" in data:
                return str(data["pagetitle"])
            if "title" in data:
                return str(data["title"])
        return None
    except ImportError:
        pass

    # Regex-based fallback
    pagetitle_match = re.search(r'^pagetitle:\s*["\']?(.+?)["\']?\s*$', frontmatter, re.MULTILINE)
    if pagetitle_match:
        return pagetitle_match.group(1).strip().strip("'\"")
    title_match = re.search(r'^title:\s*["\']?(.+?)["\']?\s*$', frontmatter, re.MULTILINE)
    if title_match:
        return title_match.group(1).strip().strip("'\"")
    return None


@dataclass
class SidebarEntry:
    """A page discovered from a sidebar, with optional section grouping."""

    section: "str | None"
    file_path: str


def walk_sidebar(
    contents: list,
    parent_section: "str | None" = None,
    _seen: "set[str] | None" = None,
) -> Iterator[SidebarEntry]:
    """Recursively walk sidebar contents, yielding SidebarEntry for each page.

    Fragment-only hrefs (e.g. /layouts/navbars/index.html#section) are resolved
    to their parent page so anchor-grouped content is still included.
    """
    if _seen is None:
        _seen = set()
    for entry in contents:
        if isinstance(entry, str):
            if entry not in _seen:
                _seen.add(entry)
                yield SidebarEntry(section=parent_section, file_path=entry)
        elif isinstance(entry, dict):
            if "section" in entry:
                section_name = clean_section_name(entry["section"])
                yield from walk_sidebar(
                    entry.get("contents", []),
                    parent_section=section_name,
                    _seen=_seen,
                )
            elif "href" in entry:
                href = entry["href"]
                if "#" in href:
                    page_path = href.split("#")[0].lstrip("/")
                    if page_path and page_path not in _seen:
                        _seen.add(page_path)
                        yield SidebarEntry(section=parent_section, file_path=page_path)
                else:
                    if href not in _seen:
                        _seen.add(href)
                        yield SidebarEntry(section=parent_section, file_path=href)
            elif "file" in entry:
                f = entry["file"]
                if f not in _seen:
                    _seen.add(f)
                    yield SidebarEntry(section=parent_section, file_path=f)


def file_path_to_url(file_path: str) -> str:
    """Convert a file path to a URL."""
    path = file_path.lstrip("/")
    name = Path(path).name
    if name in ("index.qmd", "index.html"):
        parent = str(Path(path).parent)
        if parent == ".":
            return BASE_URL
        return f"{BASE_URL}{parent}/"
    elif path.endswith(".qmd"):
        path = path[:-4] + ".html"
    return f"{BASE_URL}{path}"


# ---------------------------------------------------------------------------
# Site structure data classes
# ---------------------------------------------------------------------------

SIDEBAR_DISPLAY_NAMES = {
    "get-started": "Get Started",
    "components": "Components",
    "layouts": "Layouts",
    "concepts": "Concepts",
}

SKIP_SIDEBAR_IDS = {"deploy"}

API_SUBSECTIONS = [
    ("express", "Shiny Express"),
    ("core", "Shiny Core"),
    ("testing", "Testing"),
]


@dataclass
class Page:
    """A single documentation page."""

    title: str
    file_path: str
    content: str  # raw .qmd content


@dataclass
class Subsection:
    """A subsection within a section (e.g., "Inputs" within "Components")."""

    name: str
    pages: list[Page]


@dataclass
class Section:
    """A top-level section (e.g., "Get Started", "Components")."""

    name: str
    pages: list[Page]  # pages not under any subsection
    subsections: list[Subsection]


# ---------------------------------------------------------------------------
# Page loader
# ---------------------------------------------------------------------------


def _page_description(content: str) -> "str | None":
    """Extract pagedescription or description from YAML frontmatter."""
    try:
        import yaml  # type: ignore
        match = re.match(r"^---\s*\n(.*?)\n---\s*\n", content, re.DOTALL)
        if not match:
            return None
        data = yaml.safe_load(match.group(1))
        if isinstance(data, dict):
            for key in ("pagedescription", "description"):
                if key in data:
                    return str(data[key]).strip()
        return None
    except ImportError:
        pass
    match = re.match(r"^---\s*\n(.*?)\n---\s*\n", content, re.DOTALL)
    if not match:
        return None
    frontmatter = match.group(1)
    for key in ("pagedescription", "description"):
        m = re.search(rf"^{key}:\s*(.+)$", frontmatter, re.MULTILINE)
        if m:
            val = m.group(1).strip().strip("'\"")
            if val != ">":  # skip YAML block scalar indicator
                return val
    return None


def _is_listing_page(content: str) -> bool:
    """Return True if the page is a navigation hub page.

    Hub pages use pagedescription: in their frontmatter; content pages don't.
    Component detail pages also use listing: for example widgets but never
    have pagedescription:, so pagedescription: alone is the reliable signal.
    """
    match = re.match(r"^---\s*\n(.*?)\n---\s*\n", content, re.DOTALL)
    if not match:
        return False
    return bool(re.search(r"^pagedescription:", match.group(1), re.MULTILINE))


def _load_page(root: Path, file_path: str) -> "Page | None":
    """Read a .qmd file and extract its title and content."""
    clean_path = file_path.lstrip("/")
    if clean_path.endswith("/"):
        clean_path = clean_path + "index.qmd"
    elif clean_path.endswith(".html"):
        clean_path = clean_path[:-5] + ".qmd"
    full_path = root / clean_path
    if not full_path.exists() or not full_path.is_file():
        return None
    content = full_path.read_text()
    title = extract_title(content) or full_path.stem.replace("-", " ").title()
    if _is_listing_page(content):
        desc = _page_description(content) or ""
        synthetic = f"{desc}\n" if desc else ""
        return Page(title=title, file_path=clean_path, content=synthetic)
    return Page(title=title, file_path=clean_path, content=content)


# ---------------------------------------------------------------------------
# Template and API section builders
# ---------------------------------------------------------------------------


def _build_templates_section(root: Path) -> "Section | None":
    """Discover template pages by scanning templates/*/index.qmd."""
    templates_dir = root / "templates"
    if not templates_dir.exists():
        return None
    pages: list[Page] = []
    for qmd_path in sorted(templates_dir.glob("*/index.qmd")):
        rel_path = str(qmd_path.relative_to(root))
        page = _load_page(root, rel_path)
        if page:
            pages.append(page)
    if not pages:
        return None
    return Section(name="Templates", pages=pages, subsections=[])


def _build_api_sections(root: Path) -> list[Section]:
    """Build API Reference section from generated sidebar files.

    Returns an empty list if quartodoc hasn't been run yet.
    """
    try:
        import yaml  # type: ignore
    except ImportError:
        return []

    api_subsections: list[Subsection] = []
    for api_name, display_name in API_SUBSECTIONS:
        sidebar_path = root / "api" / api_name / "_sidebar.yml"
        if not sidebar_path.exists():
            # API index page only (sidebar not generated yet)
            index_page = _load_page(root, f"api/{api_name}/index.qmd")
            if index_page:
                api_subsections.append(Subsection(name=display_name, pages=[index_page]))
            continue
        with open(sidebar_path) as f:
            sidebar_config = yaml.safe_load(f)
        if not sidebar_config:
            continue
        contents = (
            sidebar_config
            if isinstance(sidebar_config, list)
            else sidebar_config.get("contents", [])
        )
        entries = list(walk_sidebar(contents))
        pages = [p for e in entries if (p := _load_page(root, e.file_path))]
        if pages:
            api_subsections.append(Subsection(name=display_name, pages=pages))

    if not api_subsections:
        return []
    return [Section(name="API Reference", pages=[], subsections=api_subsections)]


# ---------------------------------------------------------------------------
# Main site structure builder
# ---------------------------------------------------------------------------


def build_site_structure(root: Path) -> list[Section]:
    """Parse _quarto.yml and .qmd files to build ordered site structure."""
    try:
        import yaml  # type: ignore
    except ImportError:
        raise ImportError(
            "PyYAML is required for build_site_structure. Install with: pip install pyyaml"
        )

    quarto_path = root / "_quarto.yml"
    with open(quarto_path) as f:
        config = yaml.safe_load(f)

    sections: list[Section] = []

    sidebars = config.get("website", {}).get("sidebar", [])
    if not isinstance(sidebars, list):
        sidebars = [sidebars]

    for sidebar in sidebars:
        if not isinstance(sidebar, dict):
            continue
        sidebar_id = sidebar.get("id", "")
        if sidebar_id in SKIP_SIDEBAR_IDS:
            continue
        contents = sidebar.get("contents", [])
        if not contents:
            continue

        section_name = SIDEBAR_DISPLAY_NAMES.get(
            sidebar_id, sidebar_id.replace("-", " ").title()
        )
        entries = list(walk_sidebar(contents))

        top_pages: list[Page] = []
        subsection_map: dict[str, list[Page]] = {}

        for entry in entries:
            page = _load_page(root, entry.file_path)
            if page is None:
                continue
            if entry.section:
                subsection_map.setdefault(entry.section, []).append(page)
            else:
                top_pages.append(page)

        subsections = [
            Subsection(name=name, pages=pages)
            for name, pages in subsection_map.items()
        ]

        sections.append(
            Section(name=section_name, pages=top_pages, subsections=subsections)
        )

    # API Reference (from quartodoc-generated sidebars)
    sections.extend(_build_api_sections(root))

    # Templates (discovered by directory scan)
    templates_section = _build_templates_section(root)
    if templates_section:
        sections.append(templates_section)

    return sections


# ---------------------------------------------------------------------------
# Output writers
# ---------------------------------------------------------------------------


HEADER = f"# Shiny for Python\n\n> {SITE_DESCRIPTION}\n"


def _is_input_component_page(file_path: str) -> bool:
    """Return True for component detail pages under components/inputs/."""
    parts = Path(file_path).parts
    return len(parts) == 4 and parts[0] == "components" and parts[1] == "inputs"


def _first_paragraph_with_see_also(text: str) -> str:
    """Return the first non-empty paragraph plus any 'See also' lines."""
    first = ""
    for para in re.split(r"\n\n+", text.strip()):
        if para.strip():
            first = para.strip()
            break

    see_also = [
        line.strip()
        for line in text.splitlines()
        if re.match(r"^See [Aa]lso", line.strip())
    ]

    parts = [first] + see_also
    return "\n\n".join(parts) + "\n"


def generate_llms_full_txt(sections: list[Section]) -> str:
    """Generate llms-full.txt with full cleaned page content."""
    parts: list[str] = [HEADER]

    for section in sections:
        parts.append(f"\n## {section.name}\n")
        for page in section.pages:
            parts.append(f"### {page.title}\n")
            parts.append(clean_qmd_content(page.content, page.file_path))
            parts.append("---")
        for subsection in section.subsections:
            parts.append(f"\n### {subsection.name}\n")
            for page in subsection.pages:
                parts.append(f"#### {page.title}\n")
                cleaned = clean_qmd_content(page.content, page.file_path)
                if _is_input_component_page(page.file_path):
                    cleaned = _first_paragraph_with_see_also(cleaned)
                parts.append(cleaned)
                parts.append("---")

    return "\n".join(parts) + "\n"


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def main() -> None:
    root = Path(__file__).resolve().parent.parent
    print("Building site structure from _quarto.yml...")
    sections = build_site_structure(root)
    total_pages = sum(len(s.pages) + sum(len(sub.pages) for sub in s.subsections) for s in sections)
    print(f"Found {len(sections)} sections with {total_pages} pages.")

    print("Generating llms-full.txt...")
    llms_full_txt = generate_llms_full_txt(sections)
    (root / "llms-full.txt").write_text(llms_full_txt)

    print(f"Done. llms-full.txt: {len(llms_full_txt):,} bytes")


if __name__ == "__main__":
    main()
