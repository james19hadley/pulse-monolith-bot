import re

with open("src/bot/handlers/settings_keys.py", "r") as f:
    content = f.read()

# Replace assignments
content = re.sub(r"text, markup = get_control_panel_text\((callback|message)\.from_user\.id\)", r"text, markup = get_control_panel_data(\1.from_user.id)", content)

# Add get_control_panel_data
new_func = """
def get_control_panel_data(user_id: int):
    with SessionLocal() as db:
        user = get_or_create_user(db, user_id)
        text = get_control_panel_text(user)
    return text, get_settings_keyboard()

"""

content = content.replace("def get_control_panel_text(user) -> str:", new_func + "def get_control_panel_text(user) -> str:")

# Also the user asked to change target channel clear option
# Replace clear text inside get_channel_keyboard, wait that's in keyboards.py
with open("src/bot/handlers/settings_keys.py", "w") as f:
    f.write(content)

