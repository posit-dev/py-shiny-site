import glob
from pathlib import Path
from typing import Any, Iterable, List, Optional


class QuartoPrint(List[str]):
    def __init__(self, data: Iterable[str]):
        super().__init__(data)

    def __str__(self) -> str:
        return "\n".join(str(item) for item in self)

    def append_file(self, file_path: str, file_name: Optional[str] = None):
        if file_name is not None:
            self.append(f"## file: {file_name}")

        with open(file_path, "r") as app_file:
            app_contents = app_file.read()
            self.append(app_contents)


def list_files(path: str) -> List[str]:
    files = glob.glob(path + "/**", recursive=True)
    files = [file for file in files if not glob.os.path.isdir(file)]
    return files


def include_shiny_folder(
    path: str,
    file_name: str = "app.py",
    exclusions: List[str] = [],
    components: str = "editor, viewer",
    viewer_height: str = "800",
    extra_object: Any = "",
) -> None:
    print(
        _include_shiny_folder(
            path, file_name, exclusions, components, viewer_height, extra_object
        )
    )


def _include_shiny_folder(
    path: str,
    file_name: str = "app.py",
    exclusions: List[str] = [],
    components: str = "editor, viewer",
    viewer_height: str = "800",
    extra_object: Any = "",
) -> QuartoPrint:
    folder_path = Path(__name__).parent / path

    # Start with the header
    block = QuartoPrint(
        [
            "```{shinylive-python}",
            "#| standalone: true",
            f"#| components: [{components}]",
            "#| layout: horizontal",
            f"#| viewerHeight: {viewer_height}",
        ]
    )

    # Print contents of the main application
    block.append_file(str(folder_path / file_name), None)

    exclude_list = ["__pycache__"] + [file_name] + exclusions

    files = list_files(path)

    path_list = [
        string
        for string in files
        if not any(exclusion in string for exclusion in exclude_list)
    ]

    file_names = [string.replace(f"{str(folder_path)}/", "") for string in path_list]

    # Additional files need to start with ## file:
    for x, y in zip(path_list, file_names):
        block.append_file(x, y)

    # Finish with the closing tag
    block.append("```")
    return block


def express_tabs(path: str) -> None:
    block = QuartoPrint(
        [
            "::: {.panel-tabset group='express-switcher'}",
            "## Express",
        ]
    )
    block.extend(_include_shiny_folder(path, "express.py", exclusions=["classic.py"]))
    block.append("## Classic")
    block.extend(
        _include_shiny_folder(
            path,
            "classic.py",
            exclusions=["express.py"],
        )
    )

    block.append(":::")
    print(block)
