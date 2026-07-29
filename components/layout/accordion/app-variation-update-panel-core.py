from shiny import App, reactive, ui


def make_panel(letter):
    return ui.accordion_panel(
        f"Section {letter}",
        f"Some narrative for section {letter}",
        value=f"sec_{letter}",
    )


app_ui = ui.page_fluid(
    ui.input_switch("update_panel", "Update (and open) sections"),
    ui.accordion(*[make_panel(letter) for letter in "ABC"], id="acc", multiple=True),
)


def server(input, output, session):
    @reactive.effect
    @reactive.event(input.update_panel)
    def _():
        txt = " (updated)" if input.update_panel() else ""
        show = bool(input.update_panel() % 2 == 1)
        for letter in "ABC":
            ui.update_accordion_panel(  # <<
                "acc",
                f"sec_{letter}",
                f"Some{txt} narrative for section {letter}",
                title=f"Section {letter}{txt}",
                show=show,
            )


app = App(app_ui, server)
