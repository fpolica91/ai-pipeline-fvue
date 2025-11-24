import sqlite3
from config import DB_PATH

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

cursor.execute('''
  CREATE TABLE jobs (
      id TEXT PRIMARY KEY,
      lia_image_key TEXT NOT NULL,
      target_image_key TEXT NOT NULL,
      wavespeed_result_url TEXT,
      r2_image_key TEXT,
      r2_presigned_url TEXT,
      url_expires_at TIMESTAMP,
      status TEXT DEFAULT 'pending',
      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
  );
  ''')

conn.commit()
conn.close()