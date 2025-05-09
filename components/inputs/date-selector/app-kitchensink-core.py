from datetime import date

from shiny import App, render, ui

app_ui = ui.page_fluid(
    ui.panel_title("Date Input Parameters Demo"),
    ui.layout_column_wrap(
        # Basic date input example
        ui.card(
            ui.card_header("Default date input"),
            ui.input_date("date1", "", value="2024-01-01"),
            ui.output_text("selected_date1"),
        ),
        # Date input with minimum and maximum date constraints
        ui.card(
            ui.card_header("Date input with min/max"),
            ui.input_date(
                "date2",
                "",
                value=date(2024, 1, 1),
                min="2024-01-01",
                max="2024-12-31",
            ),
            ui.output_text("selected_date2"),
        ),
        # Date input with custom date format
        ui.card(
            ui.card_header("Custom format (mm/dd/yy)"),
            ui.input_date(
                "date3",
                "",
                value="2024-01-01",
                format="mm/dd/yy",
            ),
            ui.output_text("selected_date3"),
        ),
        # Date input that opens to decade view
        ui.card(
            ui.card_header("Start in decade view"),
            ui.input_date("date4", "", value="2024-01-01", startview="decade"),
            ui.output_text("selected_date4"),
        ),
        # Date input with week starting on Monday
        ui.card(
            ui.card_header("Week starts on Monday"),
            ui.input_date("date5", "", value="2024-01-01", weekstart=1),
            ui.output_text("selected_date5"),
        ),
        # Date input with German language localization
        ui.card(
            ui.card_header("German language"),
            ui.input_date("date6", "", value="2024-01-01", language="de"),
            ui.output_text("selected_date6"),
        ),
        # Date input with custom width
        ui.card(
            ui.card_header("Custom width"),
            ui.input_date("date7", "", value="2024-01-01", width="400px"),
            ui.output_text("selected_date7"),
        ),
        # Date input where calendar doesn't auto-close
        ui.card(
            ui.card_header("Autoclose disabled"),
            ui.input_date("date8", "", value="2024-01-01", autoclose=False),
            ui.output_text("selected_date8"),
        ),
        # Date input with specific dates disabled
        ui.card(
            ui.card_header("Specific dates disabled"),
            ui.input_date(
                "date9",
                "",
                value="2024-01-01",
                datesdisabled=["2024-01-15", "2024-01-16", "2024-01-17"],
            ),
            ui.output_text("selected_date9"),
        ),
        # Date input with weekend days disabled
        ui.card(
            ui.card_header("Weekends disabled"),
            ui.input_date(
                "date10",
                "",
                value="2024-01-01",
                daysofweekdisabled=[0, 6],  # 0 = Sunday, 6 = Saturday
            ),
            ui.output_text("selected_date10"),
        ),
        width="300px",
    ),
)


def server(input, output, session):
    # Server functions remain unchanged
    @render.text
    def selected_date1():
        return f"Selected date: {input.date1()}"

    @render.text
    def selected_date2():
        return f"Selected date: {input.date2()}"

    @render.text
    def selected_date3():
        return f"Selected date: {input.date3()}"

    @render.text
    def selected_date4():
        return f"Selected date: {input.date4()}"

    @render.text
    def selected_date5():
        return f"Selected date: {input.date5()}"

    @render.text
    def selected_date6():
        return f"Selected date: {input.date6()}"

    @render.text
    def selected_date7():
        return f"Selected date: {input.date7()}"

    @render.text
    def selected_date8():
        return f"Selected date: {input.date8()}"

    @render.text
    def selected_date9():
        return f"Selected date: {input.date9()}"

    @render.text
    def selected_date10():
        return f"Selected date: {input.date10()}"


app = App(app_ui, server)
