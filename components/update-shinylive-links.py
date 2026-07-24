import logging
import os
import sys

import shinylive
from _qmd import get_qmd_split, write_qmd

lg = logging.getLogger("shinylive")
if len(lg.handlers) == 0:
    formatter = logging.Formatter("%(levelname)s %(message)s")
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    lg.addHandler(console_handler)
    lg.setLevel(logging.INFO)


def find_index_qmds(dirs):
    index_qmds = []

    for dir in dirs:
        cdirs = [os.path.join(dir, p) for p in os.listdir(dir)]
        cdirs = [p for p in cdirs if os.path.isdir(p)]
        for cdir in cdirs:
            if ".ruff_cache" in cdir:
                continue
            index_qmds.append(os.path.join(cdir, "index.qmd"))

    return index_qmds


def check_for_shinylive_url_problems(index_qmds):
    """
    Some shinylive apps have multiple files, make sure I haven't missed those.
    """
    for qmd in index_qmds:
        meta, body = get_qmd_split(qmd)

        if "listing" not in meta:
            continue

        for item in meta["listing"]:
            if item["id"] == "relevant-functions":
                continue

            if item["id"] == "example":
                for app in item["contents"]:
                    if "shinylive" in app:
                        bundle = shinylive.decode_shinylive_url(app["shinylive"])
                        if len(bundle) > 1 and "resources" not in app:
                            lg.warning(
                                f"Multiple files in app: {qmd} - Example - {app['title']}"
                            )
            elif item["id"] == "variations" or item["id"].startswith("variation-"):
                for variation in item["contents"]:
                    # Handle both nested structure (with "apps" key) and flat structure (without "apps" key)
                    if "apps" in variation:
                        # Nested structure: variation has "apps" key
                        apps = variation["apps"]
                    elif "title" in variation and "file" in variation:
                        # Flat structure: variation itself is an app
                        apps = [variation]
                    else:
                        # Unknown structure, skip
                        continue

                    for app in apps:
                        if "shinylive" in app:
                            bundle = shinylive.decode_shinylive_url(app["shinylive"])
                            if len(bundle) > 1 and "resources" not in app:
                                variation_title = variation.get("title", "Unknown")
                                lg.warning(
                                    f"Multiple files in app: {qmd} - Variation - {variation_title} - {app['title']}"
                                )


def create_shinylive_link(app, meta):
    app_file = os.path.join(meta["_dir"], app["file"])

    if "resources" not in app:
        return shinylive.url_encode(app_file, language="py")

    return shinylive.url_encode(
        app_file,
        [os.path.join(meta["_dir"], r) for r in app["resources"]],
        language="py",
    )


def rewrite_shinylive_links(qmd):
    meta, body = get_qmd_split(qmd)

    if "listing" not in meta:
        return False

    for item in meta["listing"]:
        # Handle "example" items
        if item["id"] == "example":
            for app in item["contents"]:
                if app["title"] == "Preview":
                    continue

                if "shinylive" not in app:
                    lg.warning(
                        f"Missing shinylive link: {qmd} - Example - {app['title']}"
                    )
                    continue

                app["shinylive"] = create_shinylive_link(app, meta)

        # Handle nested "variations" structure
        elif item["id"] == "variations":
            for variation in item["contents"]:
                for app in variation["apps"]:
                    if app["title"] == "Preview":
                        continue

                    if "shinylive" not in app:
                        lg.warning(
                            f"Missing shinylive link: {qmd} - Variation - {variation['title']} - {app['title']}"
                        )
                        continue

                    app["shinylive"] = create_shinylive_link(app, meta)

        # Handle individual variation items (pattern: id starts with "variation-")
        elif item["id"].startswith("variation-"):
            for variation in item["contents"]:
                # Handle both nested structure (with "apps" key) and flat structure (without "apps" key)
                if "apps" in variation:
                    # Nested structure: variation has "apps" key
                    apps = variation["apps"]
                    variation_title = variation.get("title", "Unknown")
                elif "title" in variation and "file" in variation:
                    # Flat structure: variation itself is an app
                    apps = [variation]
                    variation_title = "Flat"
                else:
                    # Unknown structure, skip
                    continue

                for app in apps:
                    if app["title"] == "Preview":
                        continue

                    if "shinylive" not in app:
                        lg.warning(
                            f"Missing shinylive link: {qmd} - Variation - {variation_title} - {app['title']}"
                        )
                        continue

                    app["shinylive"] = create_shinylive_link(app, meta)

    write_qmd((meta, body), qmd)

    return True


def rewrite_shinylive_links_all(index_qmds):
    for qmd in index_qmds:
        rewrite_shinylive_links(qmd)

    return index_qmds


def resolve_index_qmds(paths):
    """
    Map arbitrary file/dir paths to the component ``index.qmd`` they belong to.

    Accepts a component directory, an ``index.qmd``, or any file inside a
    component directory (e.g. an edited ``app-core.py``) and resolves each to
    the owning ``index.qmd``. Paths without a real ``index.qmd`` are skipped
    with a warning. Duplicates are collapsed, order preserved.
    """
    index_qmds = []
    seen = set()

    for path in paths:
        path = os.path.normpath(path)
        if os.path.isdir(path):
            qmd = os.path.join(path, "index.qmd")
        elif os.path.basename(path) == "index.qmd":
            qmd = path
        else:
            qmd = os.path.join(os.path.dirname(path), "index.qmd")

        if not os.path.isfile(qmd):
            lg.warning(f"Skipping {path}: no component index.qmd found at {qmd}")
            continue

        if qmd not in seen:
            seen.add(qmd)
            index_qmds.append(qmd)

    return index_qmds


if __name__ == "__main__":
    # With no args, rewrite links for every component page. Given one or more
    # path args (component dirs, index.qmd files, or any file inside a
    # component dir such as an edited app-*.py), rewrite only those pages.
    if len(sys.argv) > 1:
        index_qmds = resolve_index_qmds(sys.argv[1:])
    else:
        dirs = ["inputs", "outputs", "display-messages", "layout"]
        index_qmds = find_index_qmds([os.path.join("components", d) for d in dirs])

    rewrite_shinylive_links_all(index_qmds)
