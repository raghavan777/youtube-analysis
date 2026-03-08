import sqlite3
import pandas as pd
import datetime

DB_NAME = "youtube_data.db"

def init_db():
    """Initializes the SQLite database and creates the necessary tables."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Table for Channel Details
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS channels (
            channel_id TEXT PRIMARY KEY,
            title TEXT,
            subscribers INTEGER,
            views INTEGER,
            videos INTEGER,
            last_updated TIMESTAMP
        )
    ''')

    # Table for Individual Video Metrics
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS videos (
            video_id TEXT PRIMARY KEY,
            channel_id TEXT,
            title TEXT,
            published_at TIMESTAMP,
            views INTEGER,
            likes INTEGER,
            comments INTEGER,
            engagement REAL,
            FOREIGN KEY (channel_id) REFERENCES channels (channel_id)
        )
    ''')

    conn.commit()
    conn.close()

def save_channel_data(channel_id, channel_details):
    """Saves or updates channel profile metadata in the SQL database."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute('''
        INSERT OR REPLACE INTO channels 
        (channel_id, title, subscribers, views, videos, last_updated)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (
        channel_id,
        channel_details.get("title", ""),
        int(channel_details.get("subscribers", 0)),
        int(channel_details.get("views", 0)),
        int(channel_details.get("videos", 0)),
        datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ))

    conn.commit()
    conn.close()

def save_video_data(channel_id, df):
    """Saves or updates individual videos from a dataframe into the SQL database."""
    if df.empty:
        return
        
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    for _, row in df.iterrows():
        # Ensure 'video_id' exists in row, else create a fallback
        video_id = row.get("video_id", f"unknown_{row.get('title')}")
        cursor.execute('''
            INSERT OR REPLACE INTO videos 
            (video_id, channel_id, title, published_at, views, likes, comments, engagement)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            video_id,
            channel_id,
            row.get("title", ""),
            row.get("publishedAt", ""),
            int(row.get("views", 0)),
            int(row.get("likes", 0)),
            int(row.get("comments", 0)),
            float(row.get("engagement", 0.0))
        ))

    conn.commit()
    conn.close()

# Initialize DB on import
init_db()