import importlib
import os
import sys
import time
from pathlib import Path
from typing import Generator

from _qmd import get_qmd_split

compdir = Path(__file__).parent  # ./components
rootdir = compdir.parent  # repository root
cwd = Path(os.getcwd())  # current working directory
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

    destfile.parent.mkdir(parents=True, exist_ok=True)

    app_ui.save_html(destfile, libdir=relative_to(libdir, destfile.parent))


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
    try:
        # If path2 is a parent of path1, this will work, otherwise it will raise a
        # ValueError
        return path1.relative_to(path2)
    except ValueError:

        # This branch handles simple traversal upwards (e.g. a result that's entirely
        # composed of ".." components. This is the case when path1 is a child of path2.
        if path2.is_relative_to(path1):
            for i, parent in enumerate(path2.parents):
                if parent.samefile(path1):
                    return Path(*([".."] * (i + 1)))

        # Try to handle more complicated case of traversal upwards and then back down;
        # that is, a result that starts with ".." components and then has some other
        # components. Break the problem into two smaller operations: navigating upwards
        # to the nearest common ancestor, then navigating back down to path1.
        try:
            ancestor = Path(os.path.commonpath([path1, path2]))
            dots = [".."] * len(path2.relative_to(ancestor).parts)
            return Path(*dots) / path1.relative_to(ancestor)
        except ValueError:
            # Let the original error be raised
            pass

        # Our logic failed too; that's OK, there are cases that are supposed to error,
        # like paths on different drives. Raise the original exception from the built-in
        # method.
        raise


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
