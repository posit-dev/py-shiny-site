import importlib
import os
import shutil
import sys
import time
from pathlib import Path
from typing import Generator

import shiny.html_dependencies
from _qmd import get_qmd_split
from htmltools import Tag, head_content, tags

compdir = Path(__file__).parent  # ./components
rootdir = compdir.parent  # repository root
cwd = Path(os.getcwd())  # current working directory
# This directory will be where we put all the dependencies from all the
# static component examples, rather than forcing the browser to fetch
# multiple redundant copies from various subfolders.
libdir = compdir / "static" / "lib"

sys.path.insert(0, str(rootdir))


def components(path: Path) -> Generator[Path, None, None]:
    for dirpath, _dirnames, filenames in os.walk(path):
        if "index.qmd" in filenames:
            yield Path(dirpath)


def static_preview_app_files(basedir: Path) -> Generator[Path, None, None]:
    for compdir in components(basedir):
        meta, _ = get_qmd_split(compdir / "index.qmd")
        if meta.get("appPreview", {}).get("static", False):
            app_path = Path(meta["appPreview"]["file"])
            if not (rootdir / app_path).is_file():
                raise FileNotFoundError(
                    f"{rootdir / app_path} not found (referenced from {compdir / 'index.qmd'})"
                )
            yield app_path


# components/foo/bar.py => components/static/foo/bar.html
def infile_to_outfile(infile: Path) -> Path:
    if infile.parts[0] != "components":
        raise ValueError(f"Expected components/... path, got {infile}")
    return Path(infile.parts[0], "static", *infile.parts[1:]).with_suffix(".html")


def outfile_to_infile(outfile: Path) -> Path:
    if (
        len(outfile.parts) < 3
        or outfile.parts[0] != "components"
        or outfile.parts[1] != "static"
    ):
        raise ValueError(f"Expected components/static/... path, got {outfile}")
    return outfile


def render_static_preview(appfile: Path, destfile: Path, libdir: Path):
    appfile = rootdir / appfile
    destfile = rootdir / destfile

    app_mod = importlib.import_module(
        str(appfile.relative_to(cwd).with_suffix("")).replace("/", ".")
    )
    if "app_ui" not in dir(app_mod):
        raise RuntimeError(f"app_ui not found in {appfile}")
    app_ui = app_mod.app_ui

    enrich_app_ui(app_ui)

    destfile.parent.mkdir(parents=True, exist_ok=True)

    app_ui.save_html(destfile, libdir=relative_to(libdir, destfile.parent))


def enrich_app_ui(app_ui: Tag):
    """
    Need to add Shiny dependency because some inputs/outputs won't look right without
    being intialized as part of the Shiny binding process.
    """
    app_ui.append(shiny.html_dependencies.shiny_deps())
    # Don't ever show busy indication since these are static previews
    app_ui.append(shiny.ui.busy_indicators.use(spinners=False, pulse=False))
    app_ui.append(
        head_content(
            tags.script(
                """
                window.Shiny = window.Shiny || {};
                window.Shiny.createSocket = function(url) {
                    // Prevent Shiny from trying to connect to a live server
                    // by returning a dummy WebSocket object that just no-ops
                    return {
                        addEventListener: (event, callback) => {},
                        send: () => {},
                        close: () => {},
                        readyState: 0,
                        url
                    };
                };
                """
            )
        )
    )


# TODO: Remove this function once we upgrade to Python 3.12
def relative_to(path1: Path, path2: Path) -> Path:
    """
    Equivalent to `path1.relative_to(path2, walk_up=True)`, except that walk_up=True is
    only supported from Python 3.12 on and this function works on older versions. If and
    when we can assume Python 3.12, this function can be removed in favor of the
    built-in method.

    Example:
    >>> relative_to(Path("a/b/c"), Path("a/b/c/d/e"))
    Path('d/e')
    >>> relative_to(Path("a/b/c/d/e"), Path("a/b/c/d/f/g"))
    Path('../../f/g')
    """
    return Path(os.path.relpath(path1, path2))


if __name__ == "__main__":
    for app_path in static_preview_app_files(rootdir / "components"):
        html_path = infile_to_outfile(app_path)

        # # Skip if up-to-date, unless -f flag is passed
        # if html_path.stat().st_mtime > (rootdir / app_path).stat().st_mtime:
        #     continue

        print(f"{app_path}\n    Writing to {html_path}")
        start_time = time.perf_counter()
        render_static_preview(app_path, html_path, libdir)
        end_time = time.perf_counter()
        print(f"    Succeeded in {((end_time - start_time) * 1000):.2f}ms")

    # As of this writing, there's a bug in the bootstrap dependency that ships with
    # shiny in that it doesn't include all_files=True, so some font stuff is missing.
    # This code works around the bug by copying the missing files from the shiny package
    # to the static lib directory. When the bug is fixed, this code can be removed.
    for bootstrap_dir in libdir.glob("bootstrap-5.*"):
        if not bootstrap_dir.is_dir() or (bootstrap_dir / "font.css").exists():
            continue
        bootstrap_src_dir = (
            Path(list(shiny.__path__)[0]) / "www" / "shared" / "bootstrap"
        )
        if (bootstrap_src_dir / "font.css").exists():
            shutil.copyfile(bootstrap_src_dir / "font.css", bootstrap_dir / "font.css")
            shutil.copytree(bootstrap_src_dir / "fonts", bootstrap_dir / "fonts")
        break
