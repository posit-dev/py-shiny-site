import logging
import os

import yaml as yml
from _qmd import find_qmds, get_qmd_split

lg = logging.getLogger("migrate")
if len(lg.handlers) == 0:
    formatter = logging.Formatter("%(levelname)s %(message)s")
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    lg.addHandler(console_handler)
    lg.setLevel(logging.INFO)


def extract_component_parts(path):
    if isinstance(path, str):
        meta, _ = get_qmd_split(path)
    else:
        meta = path

    info = {}
    info["_slug"] = meta["_slug"]
    info["_dir"] = meta["_dir"]
    info["title"] = meta["title"]
    info["sidebar"] = "components"

    if "preview" in meta:
        info["preview"] = meta["preview"]

    if "previewapp" in meta:
        info["appPreview"] = {"code": meta["previewapp"]}

    if not "listing" in meta:
        return info

    # Find the core app from the listing keys
    listing = meta["listing"]
    if not isinstance(listing, list):
        listing = [listing]

    # if listing is an array, then it should be the component
    if isinstance(listing, list):
        for l in listing:
            if "id" in l and l["id"] == "component":
                info["relevantFunctions"] = l["contents"][0]["relevantfunctions"]
                info["example"] = {
                    "code": l["contents"][0]["code"],
                    "shinylive": l["contents"][0]["preview"],
                }

                if "height" in l["contents"][0]:
                    info["example"]["height"] = l["contents"][0]["height"]

            if "id" in l and l["id"] == "variations":
                info["variations"] = l["contents"]["variations"]
                # rename info["variations"]["preview"] to info["variations"]["shinylive"]
                for variation in info["variations"]:
                    variation["shinylive"] = variation["preview"]
                    del variation["preview"]

    return info


def write_new_component_dir(path):
    meta, body = get_qmd_split(path)
    info = extract_component_parts(meta)

    os.makedirs(info["_dir"], exist_ok=True)

    new_meta = {}
    new_meta["title"] = info["title"]
    new_meta["sidebar"] = info["sidebar"]

    # Add preview html if needed
    if "preview" in info:
        lg.info(f"{info['_slug']} has a preview")
        new_meta["preview"] = info["preview"]

    # Write out app-preview.py
    if "appPreview" in info:
        path_preview = os.path.join(info["_dir"], "app-preview.py")
        new_meta["appPreview"] = {"file": path_preview}

        with open(path_preview, "w") as f:
            f.write(info["appPreview"]["code"])

    new_meta["listing"] = []

    # Write out app-core and app-express
    if "example" in info:
        l_example = {
            "id": "example",
            "template": "../../_partials/components-detail-example.ejs",
            "template-params": {
                "dir": info["_dir"] + "/",
            },
            "contents": [],
        }

        base = {}
        if "height" in info["example"]:
            base["height"] = info["example"]["height"]
        if "shinylive" in info["example"]:
            base["shinylive"] = info["example"]["shinylive"]

        core = {"title": "Core", "file": "app-core.py"}

        express = {"title": "Express", "file": "app-express.py"}

        core.update(base)
        express.update(base)

        l_example["contents"].append(core)
        l_example["contents"].append(express)

        new_meta["listing"].append(l_example)

        path_core = os.path.join(info["_dir"], "app-core.py")
        path_express = os.path.join(info["_dir"], "app-express.py")

        with open(path_core, "w") as f:
            f.write(info["example"]["code"])

        with open(path_express, "w") as f:
            f.write("# FIXME: Rewrite as an Express app\n")
            f.write(info["example"]["code"])

    # Relevant functions
    if "relevantFunctions" in info:
        l_relevant = {
            "id": "relevant-functions",
            "template": "../../_partials/components-detail-relevant-functions.ejs",
            "template-params": {
                "dir": info["_dir"] + "/",
            },
            "contents": info["relevantFunctions"],
        }

        new_meta["listing"].append(l_relevant)

    # Write out variations
    if "variations" in info:
        l_variations = {
            "id": "variations",
            "template": "../../_partials/components-variations.ejs",
            "template-params": {
                "dir": info["_dir"] + "/",
            },
            "contents": [],
        }

        for variation in info["variations"]:
            new_var = {}
            new_var["title"] = variation["title"]
            new_var["description"] = variation["description"]

            # slugify the title
            var_slug = variation["title"].lower().replace(" ", "-").replace("/", "-")

            new_var["apps"] = [
                {
                    "title": "Core",
                    "file": f"app-variation-{var_slug}-core.py",
                    "shinylive": variation.get(
                        "shinylive", "#FIXME: Add shinylive link"
                    ),
                },
                {
                    "title": "Express",
                    "file": f"app-variation-{var_slug}-express.py",
                    "shinylive": variation.get(
                        "shinylive", "#FIXME: Add shinylive link"
                    ),
                },
            ]

            if "height" in variation:
                for app in new_var["apps"]:
                    app["height"] = variation["height"]

            l_variations["contents"].append(new_var)

            path_core = os.path.join(info["_dir"], new_var["apps"][0]["file"])
            path_express = os.path.join(info["_dir"], new_var["apps"][1]["file"])

            with open(path_core, "w") as f:
                f.write(variation["code"])

            with open(path_express, "w") as f:
                f.write("# FIXME: Rewrite as an Express app\n")
                f.write(variation["code"])

        new_meta["listing"].append(l_variations)

    # Write out index.qmd
    path_index = os.path.join(info["_dir"], "index.qmd")
    with open(path_index, "w") as f:
        f.write("---\n")
        f.write(yml.dump(new_meta, sort_keys=False, indent=2, default_flow_style=False))
        f.write("---\n\n")
        f.write(
            body.replace(
                ":::{#component}\n:::",
                ":::{#example}\n:::\n\n:::{#relevant-functions}\n:::",
            )
        )


def migrate_directory(dir, exclude=[], clean=False):
    qmd_list = find_qmds(dir, exclude)
    for qmd in qmd_list:
        lg.info(f"Processing {qmd}")
        write_new_component_dir(qmd)
        if clean:
            os.remove(qmd)
        lg.info(f"\u2713 Migrated {qmd}")


def migrate_all(dirs):
    for dir in dirs:
        lg.info(f"Migrating {dir} -------------------------")
        migrate_directory(dir)


# Step 2: Fix component previews ----------------------------------------------
def rewrite_preview_app(qmd):
    meta, body = get_qmd_split(qmd)

    if not "listing" in meta:
        return

    import shinylive._url as shlive
    from shinylive import decode_shinylive_url, encode_shinylive_url

    ex_listing = [e for e in meta["listing"] if e["id"] == "example"][0]
    examples = ex_listing["contents"]

    shinylive_urls = [e["shinylive"] for e in examples if "shinylive" in e]

    app_preview_bundle = decode_shinylive_url(shinylive_urls[0])

    preview = {"title": "Preview", "file": "app-detail-preview.py"}

    if "height" in examples[0]:
        preview["height"] = examples[0]["height"]

    with open(os.path.join(meta["_dir"], preview["file"]), "w") as f:
        f.write(shlive.create_shinylive_chunk_contents(app_preview_bundle))

    for ex in examples:
        if "height" in ex:
            del ex["height"]

    examples.insert(0, preview)

    for ex in examples:
        if ex["title"] == "Preview":
            continue
        app_path = os.path.join(meta["_dir"], ex["file"])
        ex["shinylive"] = encode_shinylive_url(app_path)

    path_index = os.path.join(meta["_dir"], "index.qmd")
    del meta["_slug"]
    del meta["_dir"]

    with open(path_index, "w") as f:
        f.write("---\n")
        f.write(yml.dump(meta, sort_keys=False, indent=2, default_flow_style=False))
        f.write("---\n\n")
        f.write(body.strip())
        f.write("\n")


def step2_migrate_dirs(dirs, exclude=[]):
    index_qmds = []

    for dir in dirs:
        cdirs = [os.path.join(dir, p) for p in os.listdir(dir)]
        cdirs = [p for p in cdirs if os.path.isdir(p)]
        for cdir in cdirs:
            index_qmds.append(os.path.join(cdir, "index.qmd"))

    for qmd in index_qmds:
        lg.info(f"Processing {qmd}")
        rewrite_preview_app(qmd)
        lg.info(f"\u2713 Migrated {qmd}")
