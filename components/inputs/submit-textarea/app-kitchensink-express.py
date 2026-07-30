from shiny.express import input, render, ui

ui.tags.head(ui.tags.title("Submit Textarea Demo"))

# Create a submit textarea with all possible parameters
ui.input_submit_textarea(
    id="message",
    label="Compose a message:",
    placeholder="Write something, then press Ctrl/Cmd + Enter...",
    value="Hello from the kitchen sink!",
    width="min(680px, 100%)",
    rows=4,
    # A task button keeps the built-in busy indicator
    button=ui.input_task_button("send", "Send", icon="📨"),
    toolbar=ui.tags.small("Shift+Enter inserts a newline", class_="text-muted"),
    submit_key="enter+modifier",
)

ui.br()
ui.h4("Submitted message:")


@render.code
def submitted():
    # The server receives no value until the first submission
    if "message" not in input:
        return "Nothing submitted yet."
    return input.message()
