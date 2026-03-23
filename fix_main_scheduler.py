import re

with open('src/main.py', 'r') as f:
    content = f.read()

# Add stale_session_killer to the imports
if 'catalyst_heartbeat' in content and 'stale_session_killer' not in content:
    content = content.replace('from src.scheduler.jobs import catalyst_heartbeat', 'from src.scheduler.jobs import catalyst_heartbeat, stale_session_killer')

# Add the job to the scheduler
if 'stale_session_killer' not in content.split('scheduler.add_job')[1:]:
    # Find where catalyst_heartbeat is added
    job_str = 'scheduler.add_job(catalyst_heartbeat, "interval", minutes=5, args=[bot])'
    new_job_str = job_str + '\n    scheduler.add_job(stale_session_killer, "interval", minutes=60, args=[bot])'
    content = content.replace(job_str, new_job_str)

with open('src/main.py', 'w') as f:
    f.write(content)
