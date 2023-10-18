import shutil
import os

from pathlib import Path

build_dir = Path("_build")

# Continue past this part only if building entire site.
if not os.getenv("QUARTO_PROJECT_RENDER_ALL"):
    exit()

# This file is here so that GitHub Pages will serve dirs that start with an
# underscore. It is needed for docs/api/_static/.
open("_build/.nojekyll", "a").close()

# Copy API reference
# shutil.copytree("py-shiny/docs/build/html", build_dir / "api")
