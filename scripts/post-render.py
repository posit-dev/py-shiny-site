import shutil
import os
import sys

from pathlib import Path

build_dir = Path(os.getenv("QUARTO_PROJECT_OUTPUT_DIR", "_build"))

# Put back the object anchors Quarto drops from the generated api/** pages. This
# runs before the render-all check on purpose: it is idempotent and costs well
# under a second, and doing it on partial renders too means `make serve` previews
# the same anchors CI gates on. See scripts/api_anchors.py.
sys.path.insert(0, str(Path(__file__).parent))
from api_anchors import ensure_api_anchors  # noqa: E402

report = ensure_api_anchors(str(build_dir))
print(
    f"post-render: restored {report.anchors_added} api anchor(s) "
    f"across {report.pages_changed} page(s)"
)

# Continue past this part only if building entire site.
if not os.getenv("QUARTO_PROJECT_RENDER_ALL"):
    exit()

# This file is here so that GitHub Pages will serve dirs that start with an
# underscore. It is needed for docs/api/_static/.
open(build_dir / ".nojekyll", "a").close()

# Copy API reference
# shutil.copytree("py-shiny/docs/build/html", build_dir / "api")
