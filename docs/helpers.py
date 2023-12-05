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


def include_shiny_folder(
    path: str,
    file_name: str = "app.py",
    exclusions: List[str] = [],
    components: str = "editor, viewer",
    viewer_height: str = "800",
    extra_object: Any = "",
) -> None:
    """
    This function allows you to include a single shiny app in a quarto document. The
    `file_name` will be used as the main `app.py` file, and all other files will be included
    in the Shinylive application.

    Args:
        path (str): The path to the Shiny application files.
        file_name (str, optional): The name of the main application file. Defaults to "app.py".
        exclusions (List[str], optional): List of files to exclude. Defaults to [].
        components (str, optional): Components to use. Defaults to "editor, viewer".
        viewer_height (str, optional): The height of the resulting Shinylive viewer. Defaults to "800".
        extra_object (Any, optional): Any extra object to include. Defaults to "".
    """
    print(
        _include_shiny_folder(
            path, file_name, exclusions, components, viewer_height, extra_object
        )
    )


def express_tabs(path: str, viewer_height: str) -> None:
    """
    This function creates a tabbed view of the Shiny Express and Classic versions.
    You should point it to a folder with two shiny app files, `express.py` which
    defines the express implementation and `classic.py` which defines the classic one.

    This function is designed to be called within a python chunk whose output is set
    to be "asis" with `#| output: asis`.

    Args:
        path (str): The path to the Shiny application files.
        viewer_height (str): The height of the resulting Shinylive viewer
    """
    block = QuartoPrint(
        [
            "::: {.panel-tabset group='express-switcher'}",
            "## Express",
        ]
    )
    block.extend(
        _include_shiny_folder(
            path,
            "app-express.py",
            exclusions=["app-classic.py"],
        )
    )
    block.append("## Classic")
    block.extend(
        _include_shiny_folder(
            path,
            "app-classic.py",
            exclusions=["app-express.py"],
        )
    )

    block.append(":::")
    print(block)
