from shiny import ui, render, App

app_ui = ui.page_fluid(
    ui.h4("Code Output Example"),
    ui.output_code("python_code"),
    ui.output_code("sql_code"),
)

def server(input, output, session):
    @render.code
    def python_code():
        return """def calculate_sum(numbers):
    total = 0
    for num in numbers:
        total += num
    return total

result = calculate_sum([1, 2, 3, 4, 5])
print(f"Sum: {result}")"""

    @render.code
    def sql_code():
        return """SELECT users.name, COUNT(orders.id) as order_count
FROM users
LEFT JOIN orders ON users.id = orders.user_id
WHERE users.active = true
GROUP BY users.name
ORDER BY order_count DESC;"""

app = App(app_ui, server)
