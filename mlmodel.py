import pandas as pd
import numpy as np
import psycopg2
import matplotlib.pyplot as plt
import seaborn as sns
from sqlalchemy import create_engine
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression, Ridge, Lasso
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import GridSearchCV
from sklearn.pipeline import Pipeline
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Log functions for record time and message for all details during this process.
def log_progress(message):
    time_format = '%Y-%h-%D-%H:%M:%S'
    now = datetime.now()
    time_strftime = now.strftime(time_format)
    with open("./data/log-file.txt",'a') as f:
        write_format = f"{time_strftime}: {message}\n"
        f.write(write_format)

log_progress("MACHINE LEARNING MODEL START.")

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

# get data from database
data = fetch_data()

# Transform Data
data = data.drop('Year', axis=1)
log_progress(f"Fetch data from PostgreSQL:\nRows = {data.shape[0]}.\nColumns = {data.shape[1]}.\n")

cols = list(data.columns)
for col in cols:
    if col[:6] == 'NY.GDP' and col != 'NY.GDP.MKTP.CD':
        data = data.drop(col, axis=1)

log_progress(f"After some transformation steps: \nRows = {data.shape[0]}.\nColumns = {data.shape[1]}.\n")


# Preprocessing Data for Linear Regression Model:
# GDP_TEST for further test model prediction
GDP_LABEL_TEST = data.loc[len(data)-1,'NY.GDP.MKTP.CD']
INPUT_TEST = data.loc[len(data)-1,:].drop('NY.GDP.MKTP.CD')
log_progress(f"GDP_LABEL_TEST = {GDP_LABEL_TEST}")
log_progress(f"INPUT_TEST =\n{INPUT_TEST}\n")

# Data Prepration
train_data = data.copy()
train_data['NY.GDP.MKTP.CD'] = train_data['NY.GDP.MKTP.CD'].shift(-1)
train_data = train_data.drop(train_data.index[-1])
log_progress(f"Standard data set :\nRows = {train_data.shape[0]}.\nColumns = {train_data.shape[1]}.")

Y = train_data['NY.GDP.MKTP.CD']
X = train_data.drop('NY.GDP.MKTP.CD', axis=1)

# Feature Selection:
for col in train_data.columns:
    if train_data.corr().loc[col,'NY.GDP.MKTP.CD'] <= 0.25:
        train_data = train_data.drop(col, axis=1)

# Split the data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, Y, test_size=0.3)

# Model training
# Initialize the Linear Regression model
model = LinearRegression()
# Train the model on the training data
log_progress("Model learning starts")
model.fit(X_train, y_train)
log_progress("Model learning ends")

#Make predictions on the test data
log_progress("Make prediction")
y_pred = model.predict(X_test)
y_pred = pd.Series(list(y_pred))
log_progress("Evaluate the model")

#Calculate Mean Squared Error (MSE) and R-squared
mse = mean_squared_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)

#Record metrics:
log_progress("Model Metrics:")
log_progress(f"Mean Squared Error: {mse}")
log_progress(f"R-squared: {r2}")
#Print model coefficients
log_progress(f"Model Coefficients: \n{model.coef_}")
log_progress(f"Model Intercept: {model.intercept_}")

print("Model completed.")


# Plot predicted value with terget value on test set:
y_test = y_test.to_list()
y_pred = list(y_pred)
plt.figure(figsize=(10, 5))
plt.scatter(1, y_pred[0], color='blue', alpha=0.7, edgecolor='k',label="Prediction")
plt.scatter(1, y_test[0], color='red', alpha=0.7, edgecolor='k', label="Target")
for i in range(1,len(y_pred)):
    plt.scatter(i+1, y_pred[i], color='blue', alpha=0.7, edgecolor='k')
    plt.scatter(i+1, y_test[i], color='red', alpha=0.7, edgecolor='k')
    #plt.plot(y_test[i], y_pred[i], color='red', linestyle='-', linewidth=1, alpha=0.7, label='Lines Connecting Points')

plt.ylabel('Target Values(Blue) and Predicted Values(Red)')
plt.xlabel('Iterative Examples on Test Set')
plt.title('Scatter Plot of Predicted Values and Target Values')
plt.grid(True)
plt.legend()
plt.savefig('./images/test_set_ML.png', format='png', dpi=300, bbox_inches='tight')
plt.close()
log_progress("Save test_set_ML.png Successfully.")


# Plot predicted value with terget value on All Dataset:
y_pred_all = model.predict(X)
y_test_all = Y.to_list()
y_pred_all = list(y_pred_all)
plt.figure(figsize=(10, 5))
plt.scatter(1, y_pred_all[0], color='blue', alpha=0.7, edgecolor='k',label="Prediction")
plt.scatter(1, y_test_all[0], color='red', alpha=0.7, edgecolor='k', label="Target")
for i in range(1,len(y_pred_all)):
    plt.scatter(i+1, y_pred_all[i], color='blue', alpha=0.7, edgecolor='k')
    plt.scatter(i+1, y_test_all[i], color='red', alpha=0.7, edgecolor='k')
    #plt.plot(y_test[i], y_pred[i], color='red', linestyle='-', linewidth=1, alpha=0.7, label='Lines Connecting Points')

plt.ylabel('Target Values(Blue) and Predicted Values(Red)')
plt.xlabel('Iterative Examples on All Data Set')
plt.title('Scatter Plot of Predicted Values and Target Values')
plt.grid(True)
plt.legend()
plt.savefig('./images/all_set_ML.png', format='png', dpi=300, bbox_inches='tight')
plt.close()
log_progress("Save all_set_ML.png Successfully.")

# End of Machine Learning Model 
log_progress("MACHINE LEARNING MODEL END.\n")
print("Done")
