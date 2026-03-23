import re

# ------------- 1. Update config.py -------------
with open('src/core/config.py', 'r') as f:
    config_data = f.read()

config_data = config_data.replace('"Minutes before the first ping"', '"Minutes before the first ping (0 to disable)"')
with open('src/core/config.py', 'w') as f:
    f.write(config_data)

# ------------- 2. Update views.py -------------
with open('src/bot/views.py', 'r') as f:
    views_data = f.read()

views_data = views_data.replace('`{s[\'val\']}` ({s[\'desc\']})\\n', '`{s[\'val\']}` {s[\'desc\']}\\n')
with open('src/bot/views.py', 'w') as f:
    f.write(views_data)

# ------------- 3. Update jobs.py -------------
with open('src/scheduler/jobs.py', 'r') as f:
    jobs_data = f.read()

# I want to fix the `if user.catalyst_xxx else 60` to `is not None else 60` because 0 evaluates to False!
# Let's replace the whole block dynamically

old_block = """            threshold_minutes = user.catalyst_threshold_minutes if user.catalyst_threshold_minutes else 60
            interval_minutes = user.catalyst_interval_minutes if user.catalyst_interval_minutes else 20
            telegram_id = user.telegram_id
            
            if interval_minutes <= 0:
                continue # User disabled pings
                
            if now - idle_since > timedelta(minutes=threshold_minutes):
                # Check if we should ping based on interval
                last_ping_time = last_ping_timestamps.get(telegram_id)
                if last_ping_time and (now - last_ping_time) < timedelta(minutes=interval_minutes):
                    continue
                
                # Delete old ping message if exists
                if telegram_id in last_ping_message_ids:"""

new_block = """            threshold_minutes = user.catalyst_threshold_minutes if user.catalyst_threshold_minutes is not None else 60
            interval_minutes = user.catalyst_interval_minutes if user.catalyst_interval_minutes is not None else 20
            telegram_id = user.telegram_id
            
            if threshold_minutes <= 0:
                continue # User fully disabled catalyst heartbeat
                
            if now - idle_since > timedelta(minutes=threshold_minutes):
                last_ping_time = last_ping_timestamps.get(telegram_id)
                already_pinged = (last_ping_time is not None and last_ping_time >= idle_since)
                
                # Logic for interval repeat
                if interval_minutes <= 0 and already_pinged:
                    continue # Do not repeat ping
                if interval_minutes > 0 and already_pinged:
                    if (now - last_ping_time) < timedelta(minutes=interval_minutes):
                        continue # Not enough time passed for the next ping
                
                # Delete old ping message if exists
                if telegram_id in last_ping_message_ids:"""

jobs_data = jobs_data.replace(old_block, new_block)

with open('src/scheduler/jobs.py', 'w') as f:
    f.write(jobs_data)

print("done")
