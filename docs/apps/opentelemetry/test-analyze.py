import os

import logfire.db_api
import pandas as pd
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get Logfire API read token from environment
read_token = os.getenv("LOGFIRE_READ_TOKEN")
if not read_token:
    raise ValueError("LOGFIRE_READ_TOKEN not found in environment variables")

conn = logfire.db_api.connect(read_token=read_token)

# ==============================================================================
# Common Analysis Pattern: Finding Most Frequently Executed Reactive Components
# ==============================================================================
print("=== Most Frequently Executed Reactive Components ===")
query = """
SELECT
    span_name,
    COUNT(*) as execution_count,
    AVG((end_timestamp - start_timestamp)::numeric) / 1000 / 1000 as avg_duration_ms
FROM records
WHERE (span_name LIKE 'reactive.%' OR span_name LIKE 'output %')
AND start_timestamp > NOW() - INTERVAL '1 day'
GROUP BY span_name
ORDER BY avg_duration_ms DESC
LIMIT 20;
"""
df_frequent = pd.read_sql(query, conn)
print(df_frequent)
print()

# ==============================================================================
# Common Analysis Pattern: Tracking Error Rates
# ==============================================================================
print("=== Sessions with Errors ===")
query = """
SELECT
    attributes->>'session.id' as session_id,
    COUNT(*) as error_count,
    MAX(start_timestamp) as last_error
FROM records
WHERE otel_status_code = 'ERROR'
GROUP BY session_id
ORDER BY error_count DESC;
"""
df_errors = pd.read_sql(query, conn)
print(df_errors)
print()

conn.close()
