import importlib
import os
from os.path import join
from pathlib import Path
from typing import Generator

import yaml
from _qmd import get_qmd_split

compdir = Path(__file__).parent  # ./components
rootdir = compdir.parent  # repository root
cwd = Path(os.getcwd())  # current working directory
libdir = compdir / "lib"
libdir.mkdir(exist_ok=True)


def components(path: Path) -> Generator[Path, None, None]:
    for dirpath, _dirnames, filenames in os.walk(path):
        if "index.qmd" in filenames:
            yield Path(dirpath)


def static_preview_app_files(basedir: Path) -> Generator[Path, None, None]:
    for compdir in components(basedir):
        meta, _ = get_qmd_split(compdir / "index.qmd")
        if meta.get("appPreview", {}).get("static", False):
            yield rootdir / meta["appPreview"]["file"]


def render_static_preview(appfile: Path, libdir: Path):
    app_mod = importlib.import_module(
        str(appfile.relative_to(cwd).with_suffix("")).replace("/", ".")
    )
    if "app_ui" not in dir(app_mod):
        raise RuntimeError(f"app_ui not found in {appfile}")
    app_ui = app_mod.app_ui

    destfile = appfile.with_suffix(".html")
    libpath = relative_to(compdir, appfile.parent) / "lib"
    app_ui.save_html(destfile, libdir=libpath)
    print(f"Wrote {destfile.relative_to(cwd)}")


def relative_to(path1: Path, path2: Path) -> Path:
    try:
        return path1.relative_to(path2)
    except ValueError:
        if path2.is_relative_to(path1):
            for i, parent in enumerate(path2.parents):
                if parent.samefile(path1):
                    return Path(*([".."] * (i + 1)))
        raise


for static_preview_app in static_preview_app_files(rootdir / "components"):
    render_static_preview(static_preview_app, libdir)
