import psycopg2
from sqlalchemy import create_engine
import pandas as pd
from datetime import datetime
import numpy as np

# Log functions for record time and message for all details during this process.
def log_progress(message):
    time_format = '%Y-%h-%D-%H:%M:%S'
    now = datetime.now()
    time_strftime = now.strftime(time_format)
    with open("./data/log-file.txt",'a') as f:
        write_format = f"{time_strftime}: {message}\n"
        f.write(write_format)

log_progress("TESTING LOAD DATABASE START")

# Database connection parameters
user = 'postgres'
password = 'postgres'
host = 'localhost'
port = '5432'
database = 'usa_economics'
table_name_part1 = 'us_indicators_tb1_499'
table_name_part2 = 'us_indicators_tb2_500'


# Create a connection string and SQLAlchemy engine
try:
    # Create a connection string and SQLAlchemy engine
    connection_string = f"postgresql://{user}:{password}@{host}:{port}/{database}"
    engine = create_engine(connection_string)


    # SQL query
    query1 = f"SELECT * FROM {table_name_part1};"
    query2 = f"SELECT * FROM {table_name_part2};"

    # Execute query and load data into DataFrame
    df1 = pd.read_sql(query1, engine)
    df2 = pd.read_sql(query2, engine)
    log_progress("Select data from us_indicators Successfully.")

    df = pd.merge(df1, df2, left_index=True, right_index=True)

    print(df)
    print("Done")
except Exception as err:
    log_progress(f"Something went wrong. Error as {err}")
    print("Done")

"""
try:
    # This part for execute DELETE statement:
    # DELETE query
    query1 = f"DELETE FROM {table_name_part1};"
    query2 = f"DELETE FROM {table_name_part2};"
    # Create a connection --> Create a cursor object --> Commit the changes

    conn = psycopg2.connect(
        dbname=database,
        user=user,
        password=password,
        host=host,
        port=port
    )

    cursor = conn.cursor()

    cursor.execute(query1)
    cursor.execute(query2)

    conn.commit()
except Exception as err:
    log_progress(f"Something went wrong. Error as {err}")
    print("Done")
"""

log_progress("TESTING LOAD DATABASE END.\n")

