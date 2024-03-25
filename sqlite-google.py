# Import from Google Sheet
import sqlite3
import pandas as pd
import os
import weave
from weave import Dataset

weave.init('offsite-03-22/garfield')

DATASET_NAME = "billboard"

# The CSV export URL of your Google Sheet
csv_export_url = 'https://docs.google.com/spreadsheets/d/1gTdHNvDDi9AwfwA7YORMYKfY4KfjAQ2F6DoFtWySxnk/export?format=csv&gid=1094954544'

# Name of the SQLite database file
sqlite_db_path = DATASET_NAME+'.db'

# Table name in which the CSV data will be loaded
table_name = DATASET_NAME

# Fetch the CSV data from Google Sheets and load it into a pandas DataFrame
df = pd.read_csv(csv_export_url)

# SAVE DATASET TO SQLITE DB
# Connect to the SQLite database
conn = sqlite3.connect(sqlite_db_path)

# Load the DataFrame data into the SQLite table
df.to_sql(table_name, conn, if_exists='replace', index=False)

# Close the connection
conn.close()

print(f"Data from the Google Sheet has been loaded into the '{table_name}' table in the SQLite database at {sqlite_db_path}.")

# SAVE DATASET TO W&B
# Publish the dataset to W&B
weave.publish(df.values.tolist(), DATASET_NAME)

print(f"Data from the Google Sheet has been loaded into W&B.")