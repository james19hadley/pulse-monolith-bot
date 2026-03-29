with open("src/scheduler/jobs.py", "r") as f:
    content = f.read()

old_logic = """            if threshold_minutes <= 0:
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
                if telegram_id in last_ping_message_ids:
                    try:
                        if bot:
                            run_async(bot.delete_message(chat_id=telegram_id, message_id=last_ping_message_ids[telegram_id]))
                    except Exception:
                        pass
                
                hours_idle = round((now - idle_since).total_seconds() / 3600, 1)
                try:
                    if bot:
                        msg = run_async(bot.send_message(
                            chat_id=telegram_id, 
                            text=catalyst_ping_message(hours_idle)
                        ))
                        last_ping_message_ids[telegram_id] = msg.message_id
                        last_ping_timestamps[telegram_id] = now
                except Exception as e:
                    print(f"Failed to send ping to {telegram_id}: {e}")"""

new_logic = """            # Sprint 24 Guardrails Processing
            is_ping_due = False
            ping_text = ""
            
            if session.status == "active":
                if threshold_minutes <= 0:
                    continue
                if now - idle_since > timedelta(minutes=threshold_minutes):
                    # Active session idling
                    hours_idle = round((now - idle_since).total_seconds() / 3600, 1)
                    is_ping_due = True
                    ping_text = f"⏳ Слышишь, ты уже в контексте сессии {hours_idle} часа(ов) без логов. Всё еще в потоке, или пора завершить сессию?"
            elif session.status == "rest":
                # Rest mode for > 30 minutes
                if session.rest_start_time and (now - session.rest_start_time > timedelta(minutes=30)):
                    mins_rested = int((now - session.rest_start_time).total_seconds() / 60)
                    is_ping_due = True
                    # Let's not annoy them every 5 mins. Use `last_ping_timestamps` to throttle.
                    ctx_text = f" Твой Save-State: «{session.save_state_context}»." if session.save_state_context else ""
                    ping_text = f"⏸️ Перерыв затянулся: меня не было {mins_rested} минут.{ctx_text} Возвращаемся или заканчиваем на сегодня?"

            if is_ping_due:
                last_ping_time = last_ping_timestamps.get(telegram_id)
                last_event_time = session.rest_start_time if session.status == 'rest' else idle_since
                if last_event_time is None: last_event_time = now
                
                already_pinged = (last_ping_time is not None and last_ping_time >= last_event_time)
                
                # Logic for interval repeat
                if interval_minutes <= 0 and already_pinged:
                    continue
                if interval_minutes > 0 and already_pinged:
                    if (now - last_ping_time) < timedelta(minutes=interval_minutes):
                        continue
                
                if telegram_id in last_ping_message_ids:
                    try:
                        if bot:
                            run_async(bot.delete_message(chat_id=telegram_id, message_id=last_ping_message_ids[telegram_id]))
                    except Exception:
                        pass
                
                try:
                    if bot:
                        msg = run_async(bot.send_message(
                            chat_id=telegram_id, 
                            text=ping_text
                        ))
                        last_ping_message_ids[telegram_id] = msg.message_id
                        last_ping_timestamps[telegram_id] = now
                except Exception as e:
                    print(f"Failed to send ping to {telegram_id}: {e}")"""

content = content.replace(old_logic, new_logic)
with open("src/scheduler/jobs.py", "w") as f:
    f.write(content)
