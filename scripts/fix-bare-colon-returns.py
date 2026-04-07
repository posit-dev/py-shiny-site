"""
Workaround for Pandoc 3.8 (Quarto 1.9) rendering empty definition list terms as a
bare `:` on the page.

quartodoc generates Returns sections like:

    <code>[]{.parameter-name} [:]{.parameter-annotation-sep} []{.parameter-annotation}</code>

    :   A UI element.

In Pandoc 3.4, the empty-term `<code>` block was silently dropped and only the
description rendered. In Pandoc 3.8, the `:` separator inside the `<code>` term
renders literally. This script strips the empty-term line and the `:   ` prefix,
turning the block into a plain paragraph.

See docs/bare-colon-returns-issue.md for full context.
"""

import re
import sys
from pathlib import Path

EMPTY_TERM = (
    r"<code>\[\]\{\.parameter-name\}"
    r" \[:\]\{\.parameter-annotation-sep\}"
    r" \[\]\{\.parameter-annotation\}</code>"
)

PATTERN = re.compile(
    EMPTY_TERM + r"\n\n:   ",
    re.MULTILINE,
)


def fix_file(path: Path) -> bool:
    text = path.read_text(encoding="utf-8")
    fixed, count = PATTERN.subn("", text)
    if count:
        path.write_text(fixed, encoding="utf-8")
    return bool(count)


def main(api_dir: str) -> None:
    changed = 0
    for qmd in Path(api_dir).rglob("*.qmd"):
        if fix_file(qmd):
            changed += 1
    print(f"Fixed bare-colon Returns in {changed} qmd file(s).")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "./api")
