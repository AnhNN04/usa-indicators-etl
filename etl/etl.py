# Import all from other files in this folder
from datetime import datetime
import pandas as pd
import wbgapi as wb
import psycopg2
from sqlalchemy import create_engine


# Log functions for record time and message for all details during this process.
def log_progress(message):
    time_format = '%Y-%h-%D-%H:%M:%S'
    now = datetime.now()
    time_strftime = now.strftime(time_format)
    with open("./data/log-file.txt",'a') as f:
        write_format = f"{time_strftime}: {message}\n"
        f.write(write_format)

# Etract process
def extract():
    # country code for ferch data: usa, uk, br etc...
    country_code = 'USA'
    # All indicators
    # connect api and ferch data

    try:
        timein = datetime.now()
        print("This process may take a couple of mitutes for fetch all US data.")
        print("Running...")
        data = wb.data.DataFrame('all', economy=country_code)
        log_progress("API Connection Succeesfully.")
        new_data = data.transpose()
        timeout = datetime.now()
        print("Finished fetching data.")
        log_progress(f"Total fetching time: {timeout-timein}s")

        new_data.to_csv("./data/raw-data/raw-data.csv")
        log_progress("Saving raw data to raw-data.csv Successfully.")
    except Exception as error:
        log_progress(f"API Connection Fail. Error as: {error}.")

# Transform process
def transform():
    # Reading data from raw-data.csv
    df = pd.read_csv('./data/raw-data/raw-data.csv')
    # Inspecting the raw data and save into raw-inspect.txt
    with open('./data/raw-data/raw-inspect.txt','w') as file:
        file.write(f"Time: {datetime.now().strftime('%Y-%h-%D-%H:%M:%S')}.\n")
        file.write("Check the first few rows:\n")
        head = str(df.head())
        file.write(head + '\n\n')
        file.write("Summary statistics:\n")
        describe = str(df.describe())
        file.write(describe + '\n\n')
        file.write("Check for missing values:\n")
        isna = str(df.isna().sum())
        file.write(isna + '\n\n')

    # Rename columns and Set index
    df_filled = df
    df_filled = df_filled.rename(columns={'Unnamed: 0' : 'Year'})

    # Handling Missing Value: 
    #### fill missing value with mean
    cols = list(df_filled.columns)
    sum = 0
    for col in cols:
        # change datatype fo float64
        if col != "Year":
            df_filled[col] = df_filled[col].astype(float)
        # fill NaN value with mean of series
            df_filled[col].fillna(df_filled[col].mean(), inplace=True)
        # remove if all is null
        if (df_filled[col].isna().sum() != 0):
            df_filled = df_filled.drop(col, axis=1)
            sum += 1
    print(f"Total removed column: {sum}")


    # Inspecting the processed data and save to processed-inspect.txt
    with open('./data/processed-data/processed-inspect.txt','w') as file:
        file.write(f"Time: {datetime.now().strftime('%Y-%h-%D-%H:%M:%S')}.\n")
        file.write("Check the first few rows:\n")
        head = str(df_filled.head())
        file.write(head + '\n\n')
        file.write("Summary statistics:\n")
        describe = str(df_filled.describe())
        file.write(describe + '\n\n')
        file.write("Check for missing values:\n")
        isna = str(df_filled.isna().sum())
        file.write(isna + '\n\n')
    
    # Write log for data transforming process
    log_progress("Some basic transforming: Remaning, Set-index, Handle missing value,ect are Successfully.")
    
    # Saving processed-data in ./data/processed-data
    df_filled.to_csv("./data/processed-data/processed-data.csv")
    log_progress("Save processed data Successfully.")



# Load to database
def load():
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
        connection_string = f"postgresql://{user}:{password}@{host}:{port}/{database}"
        engine = create_engine(connection_string)
        log_progress("Database connection Successfully.")
    except Exception as err:
        log_progress(f"Database connection Fail. Error as: {err}.")

    # Write the DataFrame to PostgreSQL
    try:
        
        df = pd.read_csv('./data/processed-data/processed-data.csv')
        df = df.drop(columns='Unnamed: 0')
        df1 = df.iloc[:,:500]
        df1.to_sql(table_name_part1, engine, if_exists='replace', index=False)

        df2 = df.iloc[:,500:]
        df2.to_sql(table_name_part2, engine, if_exists='replace', index=False)
        
        log_progress("DataFrame inserted Successfully.")
    except Exception as err:
        print(err)
        log_progress(f"Something went wrong. Error as: {err}.")


# ETL process

try:
    log_progress("BEGINNING ETL PROCESS.")

    # extract
    log_progress("Etract processing START.")
    extract()
    log_progress("Etract processing END.")

    # transform
    log_progress("Transform processing START.")
    transform()
    log_progress("Transform processing END.")

    # load
    log_progress("Load Processing START.")
    load()
    log_progress("Load Processing END.")

    log_progress("END OF ETL PROCESS.\n")

except Exception as error:
    log_progress(error)

print("Done")

