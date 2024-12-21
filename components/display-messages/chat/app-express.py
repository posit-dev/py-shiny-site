from shiny.express import ui

ui.page_opts(
    title="Hello Shiny Chat",
    fillable=True,
    fillable_mobile=True,
)

# Create a chat instance and display it
chat = ui.Chat(id="chat")  # <<
chat.ui()  # <<


# Define a callback to run when the user submits a message
@chat.on_user_submit  # <<
async def _():  # <<
    # Simply echo the user's input back to them
    await chat.append_message(f"You said: {chat.user_input()}")  # <<
