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

# Get all spans from a specific session
session_id = "bde80eac18e14ff4206f6503d9e3a0c7b3c5f05d7dede122c0012bde986d2b87"
query = f"SELECT * FROM RECORDS WHERE attributes->>'session.id' = '{session_id}'"


df = pd.read_sql(query, conn)
print(df)

# We can also get aggregated data, e.g. number of sessions per hour
query = """
    SELECT date_trunc('hour', start_timestamp) as hour,
         COUNT(DISTINCT attributes->>'session.id') as session_count
  FROM records
  WHERE span_name = 'session.start'
  GROUP BY hour
  ORDER BY hour DESC
  LIMIT 50
"""

df_agg = pd.read_sql(query, conn)
print(df_agg)
conn.close()
