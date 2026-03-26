"""Generate llms.txt and llms-full.txt from site source files."""

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator


def clean_qmd_content(content: str) -> str:
    """Strip Quarto-specific markup from .qmd content, keeping prose and code."""
    lines = content.split("\n")
    result_lines: list[str] = []
    in_frontmatter = False
    in_raw_html_block = False
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

        # Skip Quarto div fences: ::: {.class}, ::::, ::::{.class}, bare :::
        if re.match(r"^:{3,}\s*(\{.*\})?\s*$", stripped):
            continue

        # Convert Quarto/shinylive code block syntax to standard markdown
        m = re.match(r"^```\{(shinylive-)?(\w+)\}", stripped)
        if m:
            lang = m.group(2)
            result_lines.append(f"```{lang}")
            continue

        # Remove shinylive metadata comments (#| key: value)
        if re.match(r"^#\|\s+\w+", stripped):
            continue

        # Remove inline HTML tags
        line = re.sub(r"<[^>]+>", "", line)

        # Skip lines that became empty after HTML removal (were pure HTML)
        if not line.strip() and stripped:
            continue

        result_lines.append(line)

    # Collapse 3+ consecutive blank lines to 2
    text = "\n".join(result_lines)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip() + "\n"


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


def walk_sidebar(contents: list, parent_section: "str | None" = None) -> Iterator[SidebarEntry]:
    """Recursively walk sidebar contents, yielding SidebarEntry for each page."""
    for entry in contents:
        if isinstance(entry, str):
            yield SidebarEntry(section=parent_section, file_path=entry)
        elif isinstance(entry, dict):
            if "section" in entry:
                section_name = clean_section_name(entry["section"])
                yield from walk_sidebar(entry.get("contents", []), parent_section=section_name)
            elif "href" in entry:
                href = entry["href"]
                if "#" not in href:
                    yield SidebarEntry(section=parent_section, file_path=href)
            elif "file" in entry:
                yield SidebarEntry(section=parent_section, file_path=entry["file"])


def file_path_to_url(file_path: str, base_url: str) -> str:
    """Convert a file path to a URL using the given base URL."""
    path = file_path.lstrip("/")
    name = Path(path).name
    if name in ("index.qmd", "index.html"):
        parent = str(Path(path).parent)
        if parent == ".":
            return base_url
        return f"{base_url}{parent}/"
    elif path.endswith(".qmd"):
        path = path[:-4] + ".html"
    return f"{base_url}{path}"


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


def _load_page(root: Path, file_path: str) -> "Page | None":
    """Read a .qmd file and extract its title and content."""
    clean_path = file_path.lstrip("/")
    # Convert .html refs to .qmd for reading
    if clean_path.endswith(".html"):
        clean_path = clean_path[:-5] + ".qmd"
    full_path = root / clean_path
    if not full_path.exists():
        return None
    content = full_path.read_text()
    title = extract_title(content)
    if not title:
        # Fallback to filename stem
        title = full_path.stem.replace("-", " ").title()
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
    for api_name, display_name in [
        ("express", "Shiny Express"),
        ("core", "Shiny Core"),
        ("testing", "Testing"),
    ]:
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
        pages_list: list[Page] = []
        for entry in entries:
            page = _load_page(root, entry.file_path)
            if page:
                pages_list.append(page)
        if pages_list:
            api_subsections.append(Subsection(name=display_name, pages=pages_list))

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

        # Group entries: top-level pages vs. subsection pages
        top_pages: list[Page] = []
        subsection_map: dict[str, list[Page]] = {}
        seen_subsections: list[str] = []

        for entry in entries:
            page = _load_page(root, entry.file_path)
            if page is None:
                continue
            if entry.section:
                if entry.section not in seen_subsections:
                    seen_subsections.append(entry.section)
                subsection_map.setdefault(entry.section, []).append(page)
            else:
                top_pages.append(page)

        subsections = [
            Subsection(name=name, pages=subsection_map[name])
            for name in seen_subsections
            if name in subsection_map
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
