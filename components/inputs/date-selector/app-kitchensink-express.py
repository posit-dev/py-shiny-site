from datetime import date

from shiny.express import input, render, ui

ui.page_opts(title="Date Input Parameters Demo", full_width=True)

with ui.layout_column_wrap(width="300px"):
    with ui.card(full_screen=False, height="auto"):
        ui.card_header("Default date input")
        # Basic date input
        ui.input_date("date1", "", value="2024-01-01")

        @render.text
        def selected_date1():
            return f"Selected date: {input.date1()}"

    with ui.card(full_screen=False, height="auto"):
        ui.card_header("Date input with min/max")
        # Date input with min and max dates
        ui.input_date(
            "date2",
            "",
            value=date(2024, 1, 1),
            min="2024-01-01",
            max="2024-12-31",
        )

        @render.text
        def selected_date2():
            return f"Selected date: {input.date2()}"

    with ui.card(full_screen=False, height="auto"):
        ui.card_header("Custom format (mm/dd/yy)")
        # Date input with custom format
        ui.input_date(
            "date3", "", value="2024-01-01", format="mm/dd/yy"
        )

        @render.text
        def selected_date3():
            return f"Selected date: {input.date3()}"

    with ui.card(full_screen=False, height="auto"):
        ui.card_header("Start in decade view")
        # Date input with decade view
        ui.input_date("date4", "", value="2024-01-01", startview="decade")

        @render.text
        def selected_date4():
            return f"Selected date: {input.date4()}"

    with ui.card(full_screen=False, height="auto"):
        ui.card_header("Week starts on Monday")
        # Date input with week starting on Monday
        ui.input_date("date5", "", value="2024-01-01", weekstart=1)

        @render.text
        def selected_date5():
            return f"Selected date: {input.date5()}"

    with ui.card(full_screen=False, height="auto"):
        ui.card_header("German language")
        # Date input with German language
        ui.input_date("date6", "", value="2024-01-01", language="de")

        @render.text
        def selected_date6():
            return f"Selected date: {input.date6()}"

    with ui.card(full_screen=False, height="auto"):
        ui.card_header("Custom width")
        # Date input with custom width
        ui.input_date("date7", "", value="2024-01-01", width="400px")

        @render.text
        def selected_date7():
            return f"Selected date: {input.date7()}"

    with ui.card(full_screen=False, height="auto"):
        ui.card_header("Autoclose disabled")
        # Date input with autoclose disabled
        ui.input_date("date8", "", value="2024-01-01", autoclose=False)

        @render.text
        def selected_date8():
            return f"Selected date: {input.date8()}"

    with ui.card(full_screen=False, height="auto"):
        ui.card_header("Specific dates disabled")
        # Date input with specific dates disabled
        ui.input_date(
            "date9",
            "",
            value="2024-01-01",
            datesdisabled=["2024-01-15", "2024-01-16", "2024-01-17"],
        )

        @render.text
        def selected_date9():
            return f"Selected date: {input.date9()}"

    with ui.card(full_screen=False, height="auto"):
        ui.card_header("Weekends disabled")
        # Date input with specific days of week disabled
        ui.input_date(
            "date10",
            "",
            value="2024-01-01",
            daysofweekdisabled=[0, 6],  # 0 = Sunday, 6 = Saturday
        )

        @render.text
        def selected_date10():
            return f"Selected date: {input.date10()}"
