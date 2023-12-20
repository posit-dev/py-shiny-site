# Details: For each .qmd in components folder, update the `relevantfunctions` object in the yaml front matter to contain the latest info from `func_info` filed in `./objects.json`
# Benefit: Updates the function signatures and links without doing it by hand.

import json
import os
import typing
from pathlib import PurePath

# Using `ruamel.yaml` over `yaml` as it preserves multiline strings
from ruamel.yaml import YAML

yaml = YAML()
yaml.indent(mapping=2, sequence=4, offset=2)
# Do not wrap single line strings by setting a wide width
yaml.width = 10000

base_url = "https://shiny.posit.co/py/"

with open("objects.json", "r") as file:
    quartodoc_obj = json.load(file)
if "func_info" not in quartodoc_obj.keys():
    raise TypeError(
        "./objects.json file does not contain top level key: `func_info`. Please call `make quartodoc` with an up-to-date version of py-shiny module"
    )
func_info = quartodoc_obj["func_info"]


for dir in os.listdir("components"):
    dirpath = PurePath("components") / dir
    # Only work on full folders
    if dir.startswith("_") or not os.path.isdir(dirpath):
        continue
    for subfile in os.listdir(dirpath):
        # Only work on quarto documents
        if not subfile.endswith(".qmd"):
            continue

        filepath = dirpath / subfile
        print(f"Processing: {filepath}")

        with open(filepath, "r") as file:
            lines = "".join(file.readlines())

        sep = "---\n"
        parts = lines.split(sep)
        # print(parts[1])

        frontmatter = yaml.load(parts[1])
        # print(frontmatter)

        if "listing" not in frontmatter.keys():
            print("No listing!")
            continue

        if not isinstance(frontmatter["listing"], list):
            print("frontmatter's `listing` is not an array. Upgrading!")
            frontmatter["listing"] = [frontmatter["listing"]]
        # print(frontmatter["listing"])

        for listing, listing_i in zip(
            frontmatter["listing"],
            range(len(frontmatter["listing"])),
        ):
            if not isinstance(listing, dict):
                print(listing)
                raise TypeError(
                    "{filepath} : `listing[{listing_i}]` array item received is not a `dict`. Please fix."
                )
            # print("### Listing:")
            # print(listing)
            contents_arr = listing["contents"]
            has_variations = (
                isinstance(contents_arr, dict) and "variations" in contents_arr.keys()
            )
            if has_variations:
                # Content will not have any `relevantfunctions` fields. Skip to next info
                continue

            for contents, contents_i in zip(
                contents_arr,
                range(len(contents_arr)),
            ):
                if not isinstance(contents, dict):
                    print(contents)
                    raise TypeError(
                        f"{filepath} : `listing[{listing_i}].contents[{contents_i}]` array item received is not a `dict`. Please fix."
                    )
                contents = typing.cast(dict[str, typing.Any], contents)

                # print("## Contents")
                # print(contents)
                if "relevantfunctions" not in contents.keys():
                    continue
                for relevantfunction, relevantfunction_i in zip(
                    contents["relevantfunctions"],
                    range(len(contents["relevantfunctions"])),
                ):
                    if not isinstance(relevantfunction, dict):
                        raise TypeError(
                            f"{filepath} : `listing[{listing_i}].contents[{contents_i}].relevantfunctions[{relevantfunction_i}] array item received is not a `dict`. Please fix"
                        )
                    fn_name = typing.cast(str, relevantfunction["title"])
                    if fn_name.startswith("@"):
                        fn_name = fn_name.replace("@", "")
                    if fn_name.endswith("()"):
                        fn_name = fn_name.replace("()", "")
                    # print("## Name")
                    # print(fn_name)
                    if fn_name not in func_info.keys():
                        print(
                            f"`{fn_name}` not found in quartodoc config. To update `objects.json` from the quartodoc config, please call `make quartodoc`"
                        )
                        continue

                    func_obj = func_info[fn_name]

                    # Make important function API updates
                    relevantfunction["href"] = f"{base_url}{func_obj['uri']}"
                    relevantfunction["signature"] = func_obj["signature"]
                    relevantfunction["github"] = func_obj["github"]
                    # print(relevantfunction)

        # Overwrite file with updated content
        with open(filepath, "w") as file:
            file.write(parts[0])
            file.write(sep)
            yaml.dump(frontmatter, file)
            file.write(sep)
            file.write(parts[2])
