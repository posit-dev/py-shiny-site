# Fully instrumented Shiny app with DuckDB database calls.
#
# This example demonstrates:
# 1. Shiny's built-in OpenTelemetry tracing for reactive execution
# 2. Logfire for easy OpenTelemetry setup and visualization
# 3. Custom spans for database queries
# 4. Span attributes for better observability
#
# Requirements:
#     pip install shiny logfire duckdb pandas

import os
import sys
import time
from datetime import datetime

sys.path.insert(0, os.path.dirname(__file__))
from configure import configure

configure()

import duckdb
import logfire
from opentelemetry import trace
from shiny import reactive
from shiny.express import input, render, ui

tracer = trace.get_tracer(__name__)


def init_database():
    """Initialize DuckDB database with sample products"""
    with tracer.start_as_current_span("init_database") as span:
        conn = duckdb.connect(":memory:")

        conn.execute("""
            CREATE TABLE products (
                id INTEGER PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                category VARCHAR(50) NOT NULL,
                price DECIMAL(10, 2) NOT NULL,
                stock INTEGER NOT NULL
            )
        """)

        products = [
            (1, "Laptop", "Electronics", 999.99, 15),
            (2, "Mouse", "Electronics", 29.99, 50),
            (3, "Keyboard", "Electronics", 79.99, 30),
            (4, "Desk Chair", "Furniture", 299.99, 10),
            (5, "Standing Desk", "Furniture", 599.99, 8),
            (6, "Monitor", "Electronics", 349.99, 20),
            (7, "Webcam", "Electronics", 89.99, 25),
            (8, "Bookshelf", "Furniture", 149.99, 12),
        ]

        conn.executemany("INSERT INTO products VALUES (?, ?, ?, ?, ?)", products)

        span.set_attribute("products.count", len(products))
        span.set_attribute("db.system", "duckdb")
        span.set_attribute("db.type", "in-memory")

        return conn


db_conn = init_database()

refresh_count = reactive.value(0)

ui.page_opts(title="Product Inventory - Fully Instrumented Demo")

ui.panel_title("Product Inventory - Fully Instrumented Demo")
ui.markdown(
    """
    This app demonstrates full OpenTelemetry instrumentation including:
    - Shiny session and reactive execution tracing
    - DuckDB database query tracing with custom spans
    - Custom business logic spans with attributes
    - Logfire integration for visualization
    """
)
ui.hr()


@reactive.calc
@reactive.event(input.refresh)
def increment_refresh():
    count = refresh_count() + 1
    refresh_count.set(count)
    return count


@reactive.calc
def filtered_products():
    increment_refresh()

    with tracer.start_as_current_span("filter_products") as span:
        span.set_attribute("filter.category", input.category())
        span.set_attribute("filter.min_price", input.min_price())
        span.set_attribute("filter.max_price", input.max_price())
        span.set_attribute("filter.slow_query", input.slow_query())
        span.set_attribute("db.system", "duckdb")

        if input.slow_query():
            with tracer.start_as_current_span("simulate_slow_query") as slow_span:
                slow_span.set_attribute("sleep.duration", 2.0)
                time.sleep(2)

        query = """
            SELECT id, name, category, price, stock
            FROM products
            WHERE price >= ? AND price <= ?
        """
        params = [input.min_price(), input.max_price()]

        if input.category() != "All":
            query += " AND category = ?"
            params.append(input.category())

        query += " ORDER BY name"

        with tracer.start_as_current_span("db.query") as db_span:
            db_span.set_attribute("db.system", "duckdb")
            db_span.set_attribute("db.statement", query)
            db_span.set_attribute("db.operation", "SELECT")

            with logfire.span("duckdb_query", query=query, params=params):
                result = db_conn.execute(query, params).fetchall()

            db_span.set_attribute("db.rows_returned", len(result))

        span.set_attribute("results.count", len(result))

        return result


@reactive.calc
def calculate_analytics():
    products = filtered_products()

    with tracer.start_as_current_span("calculate_analytics") as span:
        if not products:
            span.set_attribute("analytics.empty", True)
            return {
                "total_products": 0,
                "total_value": 0,
                "avg_price": 0,
                "total_stock": 0,
            }

        total_value = sum(p[3] * p[4] for p in products)
        avg_price = sum(p[3] for p in products) / len(products)
        total_stock = sum(p[4] for p in products)

        analytics = {
            "total_products": len(products),
            "total_value": total_value,
            "avg_price": avg_price,
            "total_stock": total_stock,
        }

        span.set_attribute("analytics.total_products", analytics["total_products"])
        span.set_attribute("analytics.total_value", analytics["total_value"])
        span.set_attribute("analytics.avg_price", analytics["avg_price"])
        span.set_attribute("analytics.total_stock", analytics["total_stock"])

        return analytics


with ui.layout_columns():
    with ui.card():
        ui.card_header("Filters")
        ui.input_select(
            "category",
            "Category",
            choices=["All", "Electronics", "Furniture"],
            selected="All",
        )
        ui.input_slider("min_price", "Minimum Price", 0, 1000, 0, step=50)
        ui.input_slider("max_price", "Maximum Price", 0, 1000, 1000, step=50)

    with ui.card():
        ui.card_header("Actions")
        ui.input_action_button("refresh", "Refresh Data", class_="btn-primary")
        ui.input_checkbox("slow_query", "Simulate Slow Query", value=False)

        @render.text
        def status():
            count = refresh_count()
            timestamp = datetime.now().strftime("%H:%M:%S")

            with tracer.start_as_current_span("render_status") as span:
                span.set_attribute("refresh.count", count)
                span.set_attribute("render.timestamp", timestamp)

                return f"""
Status: Active
Refreshes: {count}
Last Update: {timestamp}
Tracing: Enabled (Logfire)
DB System: DuckDB (in-memory)
Collection Level: {os.environ.get('SHINY_OTEL_COLLECT', 'default')}
                """.strip()

with ui.card():
    ui.card_header("Product Results")

    @render.data_frame
    def products_table():
        import pandas as pd

        products = filtered_products()

        if not products:
            return pd.DataFrame({"Message": ["No products found matching your criteria"]})

        return pd.DataFrame({
            "ID": [p[0] for p in products],
            "Name": [p[1] for p in products],
            "Category": [p[2] for p in products],
            "Price": [f"${p[3]:.2f}" for p in products],
            "Stock": [p[4] for p in products],
        })

with ui.card():
    ui.card_header("Analytics")

    with ui.layout_columns():
        with ui.value_box(showcase=ui.tags.i(class_="fa-solid fa-boxes-stacked")):
            "Total Products"

            @render.text
            def total_products():
                return str(calculate_analytics()["total_products"])

        with ui.value_box(showcase=ui.tags.i(class_="fa-solid fa-dollar-sign")):
            "Inventory Value"

            @render.text
            def total_value():
                return f"${calculate_analytics()['total_value']:,.2f}"

        with ui.value_box(showcase=ui.tags.i(class_="fa-solid fa-chart-line")):
            "Average Price"

            @render.text
            def avg_price():
                return f"${calculate_analytics()['avg_price']:.2f}"

        with ui.value_box(showcase=ui.tags.i(class_="fa-solid fa-warehouse")):
            "Total Stock"

            @render.text
            def total_stock():
                return str(calculate_analytics()["total_stock"])
