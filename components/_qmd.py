import os

import yaml as yml


def find_qmds(dir, exclude):
    qmd_list = [p for p in os.listdir(dir) if p.endswith(".qmd")]
    qmd_list = [os.path.join(dir, p) for p in qmd_list if p not in exclude]
    return qmd_list


def slug_from_path(path):
    return os.path.splitext(os.path.basename(path))[0]


def get_qmd_split(path):
    with open(path, "r") as f:
        lines = f.readlines()

    yaml = []
    body = []

    in_yaml = False
    found_yaml = False

    for i, line in enumerate(lines):
        # if the line starts with ---, we're in the yaml
        if line.startswith("---"):
            if found_yaml:
                body.append(line)
                continue

            if not in_yaml:
                in_yaml = True
                continue

            found_yaml = True
            in_yaml = False
            continue

        if in_yaml:
            yaml.append(line)
        else:
            body.append(line)

    meta = yml.safe_load("".join(yaml))
    if os.path.basename(path) == "index.qmd":
        meta["_slug"] = slug_from_path(os.path.dirname(path))
        meta["_dir"] = os.path.dirname(path)
    else:
        meta["_slug"] = slug_from_path(path)
        meta["_dir"] = os.path.join(os.path.dirname(path), meta["_slug"])

    return (meta, "".join(body))


def write_qmd(qmd, path):
    meta, body = qmd

    keys_rm = [key for key in meta.keys() if key.startswith("_")]

    for key in keys_rm:
        del meta[key]

    with open(path, "w") as f:
        f.write("---\n")
        f.write(yml.dump(meta, sort_keys=False, indent=2, default_flow_style=False))
        f.write("---\n\n")
        f.write(body.strip())
        f.write("\n")

    return path
