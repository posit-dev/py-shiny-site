"""Regenerate relevant-functions title/href/signature from the API pages.

With no args, rewrites every component + layout page. Given path args (dirs,
index.qmd files, or any file inside a component dir), rewrites only those pages.
Run AFTER ``make quartodoc`` (the generated api/core pages are the input).
"""

import logging
import sys

from _relevant_functions import (
    find_index_qmds,
    resolve_index_qmds,
    rewrite_relevant_functions,
)

lg = logging.getLogger("relevant-functions")
if not lg.handlers:
    h = logging.StreamHandler()
    h.setFormatter(logging.Formatter("%(levelname)s %(message)s"))
    lg.addHandler(h)
    lg.setLevel(logging.INFO)


def main(argv: list[str]) -> None:
    qmds = resolve_index_qmds(argv) if argv else find_index_qmds()
    if not argv:
        # Guard: a broken glob that silently finds nothing must not pass.
        assert len(qmds) > 40, (
            f"Expected >40 index.qmd files, found {len(qmds)}. Discovery broken?"
        )
    for qmd in qmds:
        if rewrite_relevant_functions(qmd):
            lg.info(f"updated {qmd}")


if __name__ == "__main__":
    main(sys.argv[1:])
