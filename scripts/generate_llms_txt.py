"""Generate llms.txt and llms-full.txt from site source files."""

import re


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
