import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sqlalchemy import create_engine
from datetime import datetime

# Log functions for record time and message for all details during this process.
def log_progress(message):
    time_format = '%Y-%h-%D-%H:%M:%S'
    now = datetime.now()
    time_strftime = now.strftime(time_format)
    with open("./data/log-file.txt",'a') as f:
        write_format = f"{time_strftime}: {message}\n"
        f.write(write_format)

log_progress("DASHBOARD START")

def fetch_data():
    # Database connection parameters
    user = 'postgres'
    password = 'postgres'
    host = 'localhost'
    port = '5432'
    database = 'usa_economics'
    table_name1 = 'us_indicators_tb1_499'
    table_name2 = 'us_indicators_tb2_500'

    # Create a connection string and SQLAlchemy engine
    connection_string = f"postgresql://{user}:{password}@{host}:{port}/{database}"
    engine = create_engine(connection_string)


    # SQL query
    query1 = f"SELECT * FROM {table_name1};"
    query2 = f"SELECT * FROM {table_name2};"

    # Execute query and load data into DataFrame
    df1 = pd.read_sql(query1, engine)
    df2 = pd.read_sql(query2, engine)
    
    df = pd.merge(df1, df2, left_index=True, right_index=True)
    return df

data = fetch_data()
# Transform Data
data['Year'] = data['Year'].str.replace("YR","").astype(int)
# Plot config
sns.set(style="whitegrid")
plt.grid(True)
plt.xlabel('Year')

# Plot to Time series Indicators.
# {GDP growth, Unemployment rate, Inflation rate, Federal Funds Rate, Consumer Price Index (CPI), Trade Balance} 
# GDP
plt.figure(figsize=(10, 4))
plt.xticks(ticks=data['Year'][::5], labels=data['Year'][::5])
sns.lineplot(data, x='Year', y='NY.GDP.MKTP.CD', marker='o')
plt.title('USA GDP Growth Over Time in US$')
plt.ylabel('GDP Growth')
plt.savefig('./images/gdp_plot.png', format='png', dpi=300, bbox_inches='tight')
plt.close()
log_progress("Save gdp_plot.png Successfully.")

# Unemployment Rate
plt.figure(figsize=(10, 4))
plt.xticks(ticks=data['Year'][::5], labels=data['Year'][::5])
sns.lineplot(data, x='Year', y='SL.UEM.TOTL.ZS', marker='+')
plt.title('USA Unemployment Rate Over Time in US$')
plt.ylabel('UEM (%)')
plt.savefig('./images/uem_plot.png', format='png', dpi=300, bbox_inches='tight')
plt.close()
log_progress("Save uem_plot.png Successfully.")

# Consumer Price Index
plt.figure(figsize=(10, 4))
plt.xticks(ticks=data['Year'][::5], labels=data['Year'][::5])
sns.lineplot(data, x='Year', y='FP.CPI.TOTL.ZG', marker='*')
plt.title('USA CPI Over Time in US$')
plt.ylabel('CPI')
plt.savefig('./images/cpi_plot.png', format='png', dpi=300, bbox_inches='tight')
plt.close()
log_progress("Save cpi_plot.png Successfully.")

# Consumer Price Index
plt.figure(figsize=(10, 4))
plt.xticks(ticks=data['Year'][::5], labels=data['Year'][::5])
sns.lineplot(data, x='Year', y='SP.POP.TOTL', marker='*')
plt.title('USA Population Over Time in US$')
plt.ylabel('Population')
plt.savefig('./images/pp_plot.png', format='png', dpi=300, bbox_inches='tight')
plt.close()
log_progress("Save pp_plot.png Successfully.")

log_progress("DASHBOARD END.\n")
print("Done")