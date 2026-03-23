# `01_PHILOSOPHY_AND_PSYCHOLOGY.md`

## 1. The Core Problem & Target Audience
This system is designed specifically around the psychology of an **INFJ personality type** heavily reliant on the **Fi (Introverted Feeling)** cognitive function. 

Standard productivity trackers and to-do lists fail for this psychological profile due to several critical reasons:
*   **External Control Resistance:** Traditional systems act as "managers." They require manual checkbox clicking, which feels like bureaucratic, external oversight. This creates immediate friction.
*   **The Guilt Spiral:** On "zero days" (days with no productivity), the user avoids opening the tracker to avoid the guilt of empty checkboxes. This leads to abandoning the tool entirely. 
*   **Forced Interaction:** Reporting to a rigid UI feels unnatural. The user wants to *communicate* their progress naturally, not fill out forms.

**The Solution:** The bot acts as a delegated layer of accountability. The user simply talks to the bot. The bot takes on the "burden" of tracking, updating the database, and reporting. The user never clicks a checkbox; they just exist and converse.

## 2. The Identity of "Pulse Monolith Bot"
The bot is **NOT** a humanized buddy, a cheerleader, or a secretary. 
*   **It is a Monolith:** Emotionless, dry, factual, and strictly objective. It reflects reality without judgment.
*   **It is a Catalyst:** It exists to subtly nudge the user toward action, not to serve everyday whims.
*   **No "Secretary" Features:** The bot does NOT handle requests like *"Remind me to buy milk in 2 hours."* If the user wants an alarm, they should use their phone's alarm app. The bot's sole purpose is tracking deep work and moving projects forward. It manages its own pinging schedule based on active work sessions.
*   **No "Idiot-Proofing":** We do not write extensive negative prompts (e.g., "Do not act like a weather bot"). If a user decides to use the bot to discuss the weather or chat aimlessly, the bot will simply chat back and burn the user's API tokens. The system is designed for a conscious user. We do not build defenses against misuse; we only build security for data isolation.

## 3. The "Witcher" Hierarchy of Goals (Managing 1000-Hour Epics)
A massive goal (e.g., "Spend 1000 hours to become a C++ developer") is highly demotivating if presented as a single progress bar. Seeing `1 hr / 1000 hrs` causes psychological paralysis. 

To solve this, the architecture must separate data *storage* from data *presentation*, mirroring the quest system in RPGs like *The Witcher*:
1.  **The Epic (Main Questline):** e.g., "Learn C++" (1000 hours). The database tracks this, but the bot **never** shows this massive number in daily reports to avoid demotivation. It remains hidden in the background.
2.  **The Quest (Sub-project):** e.g., "Write a text-based RPG" (30 hours). **This is the primary operational layer.** The user actively works on this. The daily report shows progress specifically for this manageable chunk (e.g., `5 hrs / 30 hrs [🟩🟩⬜⬜⬜]`).
3.  **The Next Action (Step):** e.g., "Read the chapter on Pointers" (1 hour). This is the granular action the bot uses to nudge the user during the day (*"Are you ready to spend 1 hour reading about pointers?"*).

## 4. Absolute Honesty and "The Void" (Lost Time)
The bot must track the difference between *pretending* to work and *actually* working. 
The system operates on the concept of **Sessions**. 
*   If the user starts a session that lasts 8 hours...
*   But the user only reports 3 hours of actual, focused work on projects...
*   The system mathematically calculates the remaining 5 hours.
*   These 5 hours are strictly labeled as **"The Void" (Uncategorized / Lost Time)**.

In the Evening Report, the bot will ruthlessly but objectively display this statistic: `Focused Time: 3h. Lost Time: 5h.` This acts as "kompromat" (compromising material)—a mirror reflecting the truth. It is not an insult; it is pure data to motivate the user to do better the next day.

## 5. The Rule of the "Kompromat" Report
The system is built to prevent the user from hiding. 
If the user starts a day/session but does absolutely nothing and goes silent, the system will not wait indefinitely. At a designated cutoff time (e.g., 03:00 AM), the bot will passively auto-generate the Evening Report based on whatever data it has (even if it's `Focused Time: 0`) and post it to the user's private Telegram channel. You cannot hide from the Monolith.
