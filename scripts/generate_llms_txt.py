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
