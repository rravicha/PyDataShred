import pandas as pd

# Required packages:
#   - snowflake-connector-python
#   - pandas

import snowflake.connector

# Snowflake connection parameters
conn_params = {
    "account": "VUZSETQ-MS76173",
    "user": "RRAVICHA",
    "password": "code$Mesh12345",
    "role": "ACCOUNTADMIN",
    "warehouse": "COMPUTE_WH",
    "database": "SNOWFLAKE_SAMPLE_DATA",
    "schema": "TPCH_SF1"
}

# Establish connection
conn = snowflake.connector.connect(
    account=conn_params["account"],
    user=conn_params["user"],
    password=conn_params["password"],
    role=conn_params["role"],
    warehouse=conn_params["warehouse"],
    database=conn_params["database"],
    schema=conn_params["schema"]
)

# Query to read a table (replace 'YOUR_TABLE_NAME' with the actual table name)
query = "SELECT * FROM REGION"

# Fetch data into a pandas DataFrame
df = pd.read_sql(query, conn)

# Print the DataFrame
print(df)

# Close the connection
conn.close()