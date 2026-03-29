import os
import psycopg2
conn = psycopg2.connect(dsn=os.environ['DATABASE_URL'])
cur = conn.cursor()
try:
    cur.execute("ALTER TABLE sessions ADD COLUMN rest_start_time TIMESTAMP;")
    print("Added rest_start_time")
except Exception as e:
    print(e)
    conn.rollback()

try:
    cur.execute("ALTER TABLE sessions ADD COLUMN save_state_context VARCHAR;")
    print("Added save_state_context")
except Exception as e:
    print(e)
    conn.rollback()

conn.commit()
cur.close()
conn.close()
