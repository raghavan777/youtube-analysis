import sqlite3
import pandas as pd

conn = sqlite3.connect("youtube.db")

query = """
SELECT title, views
FROM videos
ORDER BY views DESC
LIMIT 5
"""

df = pd.read_sql(query, conn)
print("Top 5 Most Viewed Videos")
print(df)


query = """
SELECT AVG(engagement) as avg_engagement
FROM videos
"""

df = pd.read_sql(query, conn)
print("Average Engagement Rate:")
print(df)
query = """
SELECT title, likes
FROM videos
ORDER BY likes DESC
LIMIT 1
"""
conn.close()