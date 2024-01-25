import logging
import os

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
            elif item["id"] == "variations":
                for variation in item["contents"]:
                    for app in variation["apps"]:
                        if "shinylive" in app:
                            bundle = shinylive.decode_shinylive_url(app["shinylive"])
                            if len(bundle) > 1 and "resources" not in app:
                                lg.warning(
                                    f"Multiple files in app: {qmd} - Variation - {variation['title']} - {app['title']}"
                                )


def create_shinylive_link(app, meta):
    app = os.path.join(meta["_dir"], app["file"])

    if "resources" not in app:
        return shinylive.encode_shinylive_url(app, language="py")

    return shinylive.encode_shinylive_url(
        app,
        [os.path.join(meta["_dir"], r) for r in app["resources"]],
        language="py",
    )


def rewrite_shinylive_links(qmd):
    meta, body = get_qmd_split(qmd)

    if "listing" not in meta:
        return False

    for item in meta["listing"]:
        if item["id"] not in ["example", "variations"]:
            continue

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

    write_qmd((meta, body), qmd)

    return True


def rewrite_shinylive_links_all(index_qmds):
    for qmd in index_qmds:
        rewrite_shinylive_links(qmd)

    return index_qmds


if __name__ == "__main__":
    dirs = ["inputs", "outputs", "display-messages"]
    index_qmds = find_index_qmds([os.path.join("components", d) for d in dirs])
    rewrite_shinylive_links_all(index_qmds)
