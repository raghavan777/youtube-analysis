import sqlite3
import pandas as pd

# Connect to database (creates file if not exists)
conn = sqlite3.connect("youtube.db")
cursor = conn.cursor()

# Create table
cursor.execute("""
CREATE TABLE IF NOT EXISTS videos (
    title TEXT,
    views INTEGER,
    likes INTEGER,
    comments INTEGER,
    engagement REAL
)
""")

conn.commit()
conn.close()

print("Database and table created successfully!")