"""Regenerate relevant-functions title/href/signature from the API pages.

With no path args, rewrites every component + layout page. Given path args
(dirs, index.qmd files, or any file inside a component dir), rewrites only
those pages. Run AFTER ``make quartodoc`` (the generated api/core pages are
the input).

Strictness (an unresolvable title = rotted/renamed export):

* ``--strict`` (default): raise, so the run fails. Used by CI, where the
  correct fields are required before merge.
* ``--no-strict``: log the unresolvable title and leave it as-authored, so a
  single rotted entry never aborts the run. Used by the build/setup chain,
  which "falls forward".
"""

import argparse
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
    parser = argparse.ArgumentParser(description=__doc__)
    strict = parser.add_mutually_exclusive_group()
    strict.add_argument(
        "--strict",
        dest="strict",
        action="store_true",
        help="raise on an unresolvable title (default; used by CI)",
    )
    strict.add_argument(
        "--no-strict",
        dest="strict",
        action="store_false",
        help="warn and leave an unresolvable title as-authored (fall forward)",
    )
    parser.set_defaults(strict=True)
    parser.add_argument("paths", nargs="*", help="dirs/files to limit the rewrite to")
    ns = parser.parse_args(argv)

    qmds = resolve_index_qmds(ns.paths) if ns.paths else find_index_qmds()
    if not ns.paths:
        # Guard: a broken glob that silently finds nothing must not pass.
        assert len(qmds) > 40, (
            f"Expected >40 index.qmd files, found {len(qmds)}. Discovery broken?"
        )
    for qmd in qmds:
        if rewrite_relevant_functions(qmd, strict=ns.strict):
            lg.info(f"updated {qmd}")


if __name__ == "__main__":
    main(sys.argv[1:])
