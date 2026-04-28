"""Generate llms-full.txt from Quarto-rendered .llms.md files."""

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator

import yaml

BASE_URL = "https://shiny.posit.co/py/"

SITE_DESCRIPTION = (
    "Shiny for Python is a framework for building reactive web applications "
    "and dashboards in pure Python. It features a reactive execution engine, "
    "built-in UI components, and support for generative AI integration."
)

# Section headings whose content (until the next heading) should be dropped.
_SKIP_SECTIONS = re.compile(r"^## (Relevant Functions|Variation Showcase)$")


def post_process_llms_md(content: str) -> str:
    """Clean a Quarto-rendered .llms.md body for LLM consumption.

    Strips directive lines, normalizes code fence tags, drops unwanted sections,
    removes bare external links and image references, and collapses excess blank lines.
    """
    lines = content.split("\n")
    result: list[str] = []
    in_code_block = False
    skip_section = False

    for line in lines:
        stripped = line.strip()

        # Strip Quarto directive lines anywhere they appear (code blocks,
        # blockquoted code blocks, Jupyter ##| syntax).
        if re.match(r"^(>\s*)*##?\|", stripped):
            continue

        if stripped.startswith("```"):
            in_code_block = not in_code_block
            if in_code_block:
                line = re.sub(r"^(```)\s*(shinylive-\w+|numberSource)\b", r"\1python", line)
            result.append(line)
            continue

        if in_code_block:
            result.append(line)
            continue

        # Entering or leaving a skipped section
        if re.match(r"^#{1,2} ", stripped):
            skip_section = bool(_SKIP_SECTIONS.match(stripped))
        if skip_section:
            continue

        # Strip bare external-link lines (navigation links, Shinylive showcases)
        # and bare image references — these are standalone lines with no prose.
        if re.match(r"^\[.*\]\(https?://", stripped):
            continue
        if re.match(r"^!\[.*\]\(", stripped):
            continue

        result.append(line)

    text = "\n".join(result)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip() + "\n"


def clean_section_name(raw: str) -> str:
    """Strip Quarto markup (images, HTML, bold wrappers) from a sidebar section name."""
    result = re.sub(r"!\[.*?\]\(.*?\)(\{.*?\})?", "", raw)
    result = re.sub(r"<span[^>]*>.*?</span>", "", result, flags=re.DOTALL)
    result = re.sub(r"<[^>]+>", "", result)
    result = re.sub(r"__(.+?)__", r"\1", result)
    result = re.sub(r"\{[^}]*\}", "", result)
    return result.strip()


def file_path_to_url(file_path: str) -> str:
    """Convert a sidebar file path to its canonical public URL under BASE_URL."""
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
    """Recursively yield a SidebarEntry for each unique page in a sidebar contents list."""
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
            elif "href" in entry or "file" in entry:
                path = entry.get("href") or entry.get("file", "")
                if "#" in path:
                    path = path.split("#")[0].lstrip("/")
                if path and path not in _seen:
                    _seen.add(path)
                    yield SidebarEntry(section=parent_section, file_path=path)


@dataclass
class Page:
    """A single documentation page."""

    title: str
    file_path: str
    content: str  # post-processed body (no leading # Title)


@dataclass
class Subsection:
    """A subsection within a section."""

    name: str
    pages: list[Page]


@dataclass
class Section:
    """A top-level section."""

    name: str
    pages: list[Page]
    subsections: list[Subsection]


def _load_page(build_dir: Path, file_path: str) -> "Page | None":
    """Read a .llms.md file and return a Page, or None if the file doesn't exist."""
    clean = file_path.lstrip("/")
    if clean.endswith("/"):
        clean += "index"
    elif clean.endswith(".html"):
        clean = clean[:-5]
    elif clean.endswith(".qmd"):
        clean = clean[:-4]
    llms_path = build_dir / (clean + ".llms.md")
    if not llms_path.exists():
        return None
    raw = llms_path.read_text()

    # Extract title from the first "# " heading that appears before any code fence.
    stem = llms_path.name.replace(".llms.md", "")
    title = stem.replace("-", " ").title()
    lines = raw.splitlines(keepends=True)
    body = raw
    for i, line in enumerate(lines):
        if line.startswith("```"):
            break  # don't look past code blocks
        if line.startswith("# "):
            title = line[2:].rstrip("\n").strip()
            body = "".join(lines[i + 1:])
            break

    return Page(
        title=title,
        file_path=file_path,
        content=post_process_llms_md(body),
    )


# ---------------------------------------------------------------------------
# Site structure constants
# ---------------------------------------------------------------------------

SIDEBAR_DISPLAY_NAMES = {
    "get-started": "Get Started",
    "components": "Components",
    "layouts": "Layouts",
    "concepts": "Concepts",
}

SKIP_SIDEBAR_IDS = {"deploy"}

_SECTION_ORDER = ["Get Started", "Concepts", "Components", "Layouts", "API Reference", "Templates"]

API_SUBSECTIONS = [
    ("express", "Shiny Express"),
    ("core", "Shiny Core"),
    ("testing", "Testing"),
]


def _build_templates_section(build_dir: Path) -> "Section | None":
    """Discover template pages by globbing _build/templates/*/index.llms.md."""
    templates_dir = build_dir / "templates"
    if not templates_dir.exists():
        return None
    pages: list[Page] = []
    for llms_path in sorted(templates_dir.glob("*/index.llms.md")):
        source_rel = str(llms_path.relative_to(build_dir)).replace(".llms.md", ".qmd")
        page = _load_page(build_dir, source_rel)
        if page:
            pages.append(page)
    if not pages:
        return None
    return Section(name="Templates", pages=pages, subsections=[])


def _build_api_sections(root: Path, build_dir: Path) -> list[Section]:
    """Build the API Reference section from each subsection's _sidebar.yml."""
    api_subsections: list[Subsection] = []
    for api_name, display_name in API_SUBSECTIONS:
        sidebar_path = root / "api" / api_name / "_sidebar.yml"
        if not sidebar_path.exists():
            index_page = _load_page(build_dir, f"api/{api_name}/index.qmd")
            if index_page:
                api_subsections.append(Subsection(name=display_name, pages=[index_page]))
            continue
        with open(sidebar_path) as f:
            sidebar_config = yaml.safe_load(f)
        if not sidebar_config:
            continue
        if isinstance(sidebar_config, list):
            contents = sidebar_config
        elif "website" in sidebar_config:
            # _quarto.yml-style: website.sidebar[0].contents
            sidebars = sidebar_config["website"].get("sidebar", [])
            if isinstance(sidebars, list) and sidebars:
                contents = sidebars[0].get("contents", [])
            else:
                contents = sidebars.get("contents", []) if isinstance(sidebars, dict) else []
        else:
            contents = sidebar_config.get("contents", [])
        index_path = f"api/{api_name}/index.qmd"
        pages = [p for e in walk_sidebar(contents) if e.file_path != index_path and (p := _load_page(build_dir, e.file_path))]
        if pages:
            api_subsections.append(Subsection(name=display_name, pages=pages))

    if not api_subsections:
        return []
    return [Section(name="API Reference", pages=[], subsections=api_subsections)]


def build_site_structure(root: Path) -> list[Section]:
    """Parse _quarto.yml and .llms.md files to build an ordered list of Sections."""
    build_dir = root / "_build"
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
            page = _load_page(build_dir, entry.file_path)
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

    sections.extend(_build_api_sections(root, build_dir))

    templates_section = _build_templates_section(build_dir)
    if templates_section:
        sections.append(templates_section)

    sections.sort(
        key=lambda s: _SECTION_ORDER.index(s.name) if s.name in _SECTION_ORDER else len(_SECTION_ORDER)
    )

    return sections


# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------

HEADER = f"# Shiny for Python\n\n> {SITE_DESCRIPTION}\n"


def generate_llms_full_txt(sections: list[Section]) -> str:
    """Render sections into the llms-full.txt string with headings, source URLs, and separators."""
    parts: list[str] = [HEADER]

    for section in sections:
        parts.append(f"\n## {section.name}\n")
        for page in section.pages:
            parts.append(f"### {page.title}\n")
            parts.append(f"Source: {file_path_to_url(page.file_path)}\n")
            parts.append(page.content)
            parts.append("---")
        for subsection in section.subsections:
            parts.append(f"\n### {subsection.name}\n")
            for page in subsection.pages:
                parts.append(f"#### {page.title}\n")
                parts.append(f"Source: {file_path_to_url(page.file_path)}\n")
                parts.append(page.content)
                parts.append("---")

    return "\n".join(parts) + "\n"


def main() -> None:
    root = Path(__file__).resolve().parent.parent
    build_dir = root / "_build"
    if not build_dir.exists():
        print("Error: _build/ directory not found. Run 'make site' first.")
        raise SystemExit(1)

    print("Building site structure from _quarto.yml...")
    sections = build_site_structure(root)
    total_pages = sum(
        len(s.pages) + sum(len(sub.pages) for sub in s.subsections)
        for s in sections
    )
    print(f"Found {len(sections)} sections with {total_pages} pages.")

    print("Generating llms-full.txt...")
    llms_full_txt = generate_llms_full_txt(sections)
    output_path = build_dir / "llms-full.txt"
    output_path.write_text(llms_full_txt)
    print(f"Done. {output_path}: {len(llms_full_txt):,} bytes")


if __name__ == "__main__":
    main()
