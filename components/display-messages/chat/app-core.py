from shiny import App, ui

app_ui = ui.page_fillable(
    ui.panel_title("Hello Shiny Chat"),
    ui.chat_ui("chat"),  # <<
    fillable_mobile=True,
)


def server(input):
    # Create a chat instance and display it
    chat = ui.Chat(id="chat")  # <<

    # Define a callback to run when the user submits a message
    @chat.on_user_submit  # <<
    async def handle_user_input(user_input: str):  # <<
        # Simply echo the user's input back to them
        await chat.append_message(f"You said: {user_input}")  # <<


app = App(app_ui, server)
