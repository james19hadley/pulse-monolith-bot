import sqlite3
import os

try:
    conn = sqlite3.connect('pulse.db')
    c = conn.cursor()
    c.execute("ALTER TABLE habits ADD COLUMN status VARCHAR DEFAULT 'active'")
    conn.commit()
    conn.close()
    print("Migration successful.")
except Exception as e:
    print("Migration failed:", e)

