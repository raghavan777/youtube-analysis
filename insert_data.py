import sqlite3
import pandas as pd

# Load CSV file
df = pd.read_csv("data/youtube_data.csv")

# Connect to database
conn = sqlite3.connect("youtube.db")

# Insert data into videos table
df.to_sql("videos", conn, if_exists="replace", index=False)

conn.commit()
conn.close()

print("Data inserted successfully!")