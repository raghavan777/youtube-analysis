import pandas as pd
import sqlite3
import matplotlib.pyplot as plt
import re  # Added for title cleaning

conn = sqlite3.connect("youtube.db")

query = """
SELECT title, views
FROM videos
ORDER BY views DESC
LIMIT 5
"""

df = pd.read_sql(query, conn)

# --- THE FIX: Remove emojis/non-ASCII characters from titles ---
df['title'] = df['title'].apply(lambda x: re.sub(r'[^\x00-\x7f]', r'', x))

plt.bar(df['title'], df['views'])
plt.xticks(rotation=45, ha='right') # 'ha' makes the rotated labels line up better
plt.title("Top 5 Most Viewed Videos")
plt.xlabel("Video Title")
plt.ylabel("Views")
plt.tight_layout()
plt.show()

conn.close()