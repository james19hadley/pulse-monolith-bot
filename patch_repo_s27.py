import re

with open("src/db/repo.py", "r") as f:
    text = f.read()

# 1. Strip SQLite habit migrations
text = re.sub(r'try:\s*conn\.execute\(sql_text\("ALTER TABLE habits ADD COLUMN.*?"\)\)\s*except Exception:\s*pass\s*', '', text)

# 2. Add SQLite project migrations
sqlite_proj_migrations = """try:
                    conn.execute(sql_text("ALTER TABLE projects ADD COLUMN daily_target_value INTEGER"))
                except Exception:
                    pass
                try:
                    conn.execute(sql_text("ALTER TABLE projects ADD COLUMN daily_progress INTEGER DEFAULT 0"))
                except Exception:
                    pass
                try:
                    conn.execute(sql_text("ALTER TABLE projects ADD COLUMN current_streak INTEGER DEFAULT 0"))
                except Exception:
                    pass
                try:
                    conn.execute(sql_text("ALTER TABLE projects ADD COLUMN last_completed_date DATE"))
                except Exception:
                    pass
                try:
                    conn.execute(sql_text("ALTER TABLE projects ADD COLUMN total_completions INTEGER DEFAULT 0"))
                except Exception:
                    pass
"""
# insert before try sessions
text = text.replace('try:\n                    conn.execute(sql_text("ALTER TABLE sessions', sqlite_proj_migrations + '                try:\n                    conn.execute(sql_text("ALTER TABLE sessions')

# 3. Strip Postgres habit migrations
text = re.sub(r'\("habits",\s*"[^"]+",\s*"[^"]+"\),?\s*', '', text)

# 4. Add Postgres project migrations
pg_proj_migrations = """("projects", "daily_target_value", "INTEGER"),
                    ("projects", "daily_progress", "INTEGER DEFAULT 0"),
                    ("projects", "current_streak", "INTEGER DEFAULT 0"),
                    ("projects", "last_completed_date", "DATE"),
                    ("projects", "total_completions", "INTEGER DEFAULT 0"),
                    """
text = text.replace('("projects", "unit", "VARCHAR"),', pg_proj_migrations + '("projects", "unit", "VARCHAR"),')

with open("src/db/repo.py", "w") as f:
    f.write(text)

print("repo.py patched.")
