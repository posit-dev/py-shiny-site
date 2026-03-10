"""
Fully instrumented Shiny app with DuckDB database calls.

This example demonstrates:
1. Shiny's built-in OpenTelemetry tracing for reactive execution
2. Logfire for easy OpenTelemetry setup and visualization
3. Custom spans for database queries
4. Span attributes for better observability

Requirements:
    pip install shiny logfire duckdb pandas
"""

import os
import time
from datetime import datetime

# Configure Logfire BEFORE importing Shiny
# This ensures the TracerProvider is set up before Shiny initializes
import logfire

# Configure Logfire (it will auto-configure on first use if needed)
logfire.configure()

# Set Shiny's OpenTelemetry collection level
# Options: 'none', 'session', 'reactive_update', 'reactivity', 'all'
os.environ["SHINY_OTEL_COLLECT"] = "reactivity"

# Import Shiny after OpenTelemetry is configured
from shiny import App, reactive, render, ui
from opentelemetry import trace
import duckdb

# Get tracer for custom spans
tracer = trace.get_tracer(__name__)


def init_database():
    """Initialize DuckDB database with sample products"""
    with tracer.start_as_current_span("init_database") as span:
        conn = duckdb.connect(":memory:")

        # Create products table
        conn.execute("""
            CREATE TABLE products (
                id INTEGER PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                category VARCHAR(50) NOT NULL,
                price DECIMAL(10, 2) NOT NULL,
                stock INTEGER NOT NULL
            )
        """)

        # Insert sample data
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

        conn.executemany(
            "INSERT INTO products VALUES (?, ?, ?, ?, ?)", products
        )

        span.set_attribute("products.count", len(products))
        span.set_attribute("db.system", "duckdb")
        span.set_attribute("db.type", "in-memory")

        return conn


# Initialize the database connection
db_conn = init_database()


# UI Definition
app_ui = ui.page_fluid(
    ui.panel_title("Product Inventory - Fully Instrumented Demo"),
    ui.markdown(
        """
        This app demonstrates full OpenTelemetry instrumentation including:
        - Shiny session and reactive execution tracing
        - DuckDB database query tracing with custom spans
        - Custom business logic spans with attributes
        - Logfire integration for visualization
        """
    ),
    ui.hr(),
    ui.layout_columns(
        ui.card(
            ui.card_header("Filters"),
            ui.input_select(
                "category",
                "Category",
                choices=["All", "Electronics", "Furniture"],
                selected="All",
            ),
            ui.input_slider("min_price", "Minimum Price", 0, 1000, 0, step=50),
            ui.input_slider("max_price", "Maximum Price", 0, 1000, 1000, step=50),
        ),
        ui.card(
            ui.card_header("Actions"),
            ui.input_action_button("refresh", "Refresh Data", class_="btn-primary"),
            ui.input_checkbox("slow_query", "Simulate Slow Query", value=False),
            ui.output_text_verbatim("status"),
        ),
    ),
    ui.card(
        ui.card_header("Product Results"),
        ui.output_data_frame("products_table"),
    ),
    ui.card(
        ui.card_header("Analytics"),
        ui.output_ui("analytics"),
    ),
)


def server(input, output, session):
    # Reactive value to track refresh count
    refresh_count = reactive.value(0)

    @reactive.calc
    @reactive.event(input.refresh)
    def increment_refresh():
        """Track how many times user refreshed"""
        count = refresh_count() + 1
        refresh_count.set(count)
        return count

    @reactive.calc
    def filtered_products():
        """Query DuckDB database with filters - traced with custom spans"""
        # Trigger on refresh button
        increment_refresh()

        # Create custom span for business logic
        with tracer.start_as_current_span("filter_products") as span:
            # Add filter parameters as span attributes
            span.set_attribute("filter.category", input.category())
            span.set_attribute("filter.min_price", input.min_price())
            span.set_attribute("filter.max_price", input.max_price())
            span.set_attribute("filter.slow_query", input.slow_query())
            span.set_attribute("db.system", "duckdb")

            # Simulate slow query if requested
            if input.slow_query():
                with tracer.start_as_current_span("simulate_slow_query") as slow_span:
                    slow_span.set_attribute("sleep.duration", 2.0)
                    time.sleep(2)

            # Build query with parameterization
            query = """
                SELECT id, name, category, price, stock
                FROM products
                WHERE price >= ? AND price <= ?
            """
            params = [input.min_price(), input.max_price()]

            # Add category filter if needed
            if input.category() != "All":
                query += " AND category = ?"
                params.append(input.category())

            query += " ORDER BY name"

            # Execute query with custom span
            with tracer.start_as_current_span("db.query") as db_span:
                db_span.set_attribute("db.system", "duckdb")
                db_span.set_attribute("db.statement", query)
                db_span.set_attribute("db.operation", "SELECT")

                # Use Logfire's span to also capture the query
                with logfire.span("duckdb_query", query=query, params=params):
                    result = db_conn.execute(query, params).fetchall()

                db_span.set_attribute("db.rows_returned", len(result))

            span.set_attribute("results.count", len(result))

            return result

    @reactive.calc
    def calculate_analytics():
        """Calculate analytics from filtered results"""
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

            total_value = sum(p[3] * p[4] for p in products)  # price * stock
            avg_price = sum(p[3] for p in products) / len(products)  # price
            total_stock = sum(p[4] for p in products)  # stock

            analytics = {
                "total_products": len(products),
                "total_value": total_value,
                "avg_price": avg_price,
                "total_stock": total_stock,
            }

            # Add analytics as span attributes
            span.set_attribute("analytics.total_products", analytics["total_products"])
            span.set_attribute("analytics.total_value", analytics["total_value"])
            span.set_attribute("analytics.avg_price", analytics["avg_price"])
            span.set_attribute("analytics.total_stock", analytics["total_stock"])

            return analytics

    @render.data_frame
    def products_table():
        """Display filtered products"""
        import pandas as pd

        products = filtered_products()

        if not products:
            return pd.DataFrame({"Message": ["No products found matching your criteria"]})

        # Format for display (products is list of tuples: id, name, category, price, stock)
        return pd.DataFrame({
            "ID": [p[0] for p in products],
            "Name": [p[1] for p in products],
            "Category": [p[2] for p in products],
            "Price": [f"${p[3]:.2f}" for p in products],
            "Stock": [p[4] for p in products],
        })

    @render.ui
    def analytics():
        """Display analytics"""
        stats = calculate_analytics()

        if stats["total_products"] == 0:
            return ui.p("No products to analyze")

        return ui.TagList(
            ui.layout_columns(
                ui.value_box(
                    "Total Products",
                    stats["total_products"],
                    showcase=ui.tags.i(class_="fa-solid fa-boxes-stacked"),
                ),
                ui.value_box(
                    "Inventory Value",
                    f"${stats['total_value']:,.2f}",
                    showcase=ui.tags.i(class_="fa-solid fa-dollar-sign"),
                ),
                ui.value_box(
                    "Average Price",
                    f"${stats['avg_price']:.2f}",
                    showcase=ui.tags.i(class_="fa-solid fa-chart-line"),
                ),
                ui.value_box(
                    "Total Stock",
                    stats["total_stock"],
                    showcase=ui.tags.i(class_="fa-solid fa-warehouse"),
                ),
            )
        )

    @render.text
    def status():
        """Display current status"""
        count = refresh_count()
        timestamp = datetime.now().strftime("%H:%M:%S")

        # Add a custom event to Logfire
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


app = App(app_ui, server)


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("Fully Instrumented Shiny App with DuckDB")
    print("=" * 60)
    print("\nOpenTelemetry Configuration:")
    print(f"  Collection Level: {os.environ.get('SHINY_OTEL_COLLECT', 'default')}")
    print("  DuckDB: Custom span instrumentation")
    print("  Logfire: Configured")
    print("\nView traces at: https://logfire.pydantic.dev/")
    print("\nWhat's traced:")
    print("  ✓ Session lifecycle")
    print("  ✓ Reactive calculations and renders")
    print("  ✓ Database queries (DuckDB with custom spans)")
    print("  ✓ Custom business logic spans")
    print("  ✓ Span attributes for filtering/analysis")
    print("=" * 60 + "\n")
