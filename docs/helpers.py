import glob
from pathlib import Path
from typing import Any, Iterable, List, Literal, Optional, Sequence

from shinylive import ShinyliveApp


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

    def append_shinylive_chunk(
        self,
        files: list[str] | str,
        language: str = "py",
        **kwargs,
    ):
        if isinstance(files, str):
            app_file = files
            files = []
        else:
            app_file = files.pop(0)

        app = ShinyliveApp.from_local(app_file, files, language)

        self.append(app.chunk(**kwargs))


def shinylive_chunk(
    contents: list[str] | str,
    components: Sequence[str] = ("editor", "viewer"),
    viewer_height: str = "400",
    layout: Literal["horizontal", "vertical"] = "horizontal",
):
    block = QuartoPrint(
        [
            "```{shinylive-python}",
            "#| standalone: true",
            f"#| components: [{', '.join(components)}]",
            f"#| layout: {layout}",
            f"#| viewerHeight: {viewer_height}",
            "",
        ]
    )

    if isinstance(contents, str):
        block.append(contents.strip())
    else:
        block.extend(contents)

    block.append("```")
    return block


def list_files(path: str) -> List[str]:
    files = glob.glob(path + "/**", recursive=True)
    files = [file for file in files if not glob.os.path.isdir(file)]
    return files


def _include_shiny_folder(
    path: str,
    file_name: str = "app.py",
    exclusions: List[str] = [],
    components: Sequence[str] = ("editor", "viewer"),
    viewer_height: str = "800",
    extra_object: Any = "",
) -> QuartoPrint:
    folder_path = Path(__name__).parent / path

    # Start with the header
    block = QuartoPrint(
        [
            "```{shinylive-python}",
            "#| standalone: true",
            f"#| components: [{', '.join(components)}]",
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


def express_editor_tabs(path: str, viewer_height: str = "400px") -> None:
    """
    This function creates a tabbed view of the Shiny Express and Core versions.
    You should point it to a folder with two shiny app files, `app-express.py` which
    defines the express implementation and `app-core.py` which defines the core one.

    This function is designed to be called within a python chunk whose output is set
    to be "asis" with `#| output: asis`.

    Args:
        path (str): The path to the Shiny application files.
        viewer_height (str): The height of the resulting Shinylive viewer
    """
    block = QuartoPrint(
        [
            "::: {.panel-tabset .shiny-mode-tabset group='shiny-app-mode'}",
            "## Express",
        ]
    )
    block.extend(
        _include_shiny_folder(
            path,
            "app-express.py",
            exclusions=["app-core.py"],
        )
    )
    block.append("## Core")
    block.extend(
        _include_shiny_folder(
            path,
            "app-core.py",
            exclusions=["app-express.py"],
        )
    )

    block.append(":::")
    print(block)


def shinylive_app_preview(
    files: list[str] | str,
    viewer_height: str | int = 400,
    div_attrs="",
    **kwargs,
) -> None:
    block = QuartoPrint([f"::: {{.app-preview {div_attrs}}}"])

    block.append_shinylive_chunk(
        files,
        viewer_height=str(viewer_height),
        components=["viewer"],
        **kwargs,
    )

    block.append(":::")
    print(block)


def express_core_preview(
    app_express: str | None = None,
    app_core: str | None = None,
    files: list[str] | str | None = None,
    div_attrs=".shiny-mode-tabset",
    group="shiny-app-mode",
    language="py",
    **kwargs,
) -> None:
    if app_express is None and app_core is None:
        return

    if files is None:
        files = []
    elif isinstance(files, str):
        files = [files]

    header_attrs = ".panel-tabset"
    header_attrs += " " + div_attrs if div_attrs else ""
    header_attrs += f" group='{group}'" if group else ""

    block = QuartoPrint(["::: {" + header_attrs + "}"])

    apps = zip([app_express, app_core], ["Express", "Core"])

    for app_file, tab_name in apps:
        if app_file is None:
            continue

        sl_app = ShinyliveApp.from_local(app_file, files, language)

        block.append("### " + tab_name)
        block.append(
            '```{.python .code-overflow-scroll shinylive="' + sl_app.url() + '"}'
        )
        block.append_file(app_file)
        block.extend(["```", ""])

    block.append(":::")
    print(block)
