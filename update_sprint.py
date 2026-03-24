with open("docs/sprints/16_UX_ONBOARDING_KEYBOARDS.md", "r") as f:
    text = f.read()

new_text = text.replace("- [ ] Rewrite `welcome_message`", "- [x] Rewrite `welcome_message`")
new_text = new_text.replace("- [ ] Add the hardcoded language disclaimer", "- [x] Add the hardcoded language disclaimer")
new_text = new_text.replace("- [ ] Provide clear, hardcoded examples", "- [x] Provide clear, hardcoded examples")
new_text = new_text.replace("- [ ] Create `src/bot/keyboards.py`", "- [x] Create `src/bot/keyboards.py`")
new_text = new_text.replace("- [ ] Implement a persistent Reply Keyboard", "- [x] Implement a persistent Reply Keyboard")
new_text = new_text.replace("- [ ] Define FSM states", "- [x] Define FSM states")
new_text = new_text.replace("- [ ] Refactor the `/add_key` handler", "- [x] Refactor the API Key handler with inline menus\\n- [x] Create interactive menus for Persona, Timezone, and Reports")

new_tasks = """
### 4. Advanced Settings Inline Menus
- [ ] Add `set_catalyst` inline menus and FSM text inputs (15/30/60/120 min or custom text).
- [ ] Add `set_interval` inline menus and FSM text inputs.
- [ ] Add `set_channel` sub-menu and listener to parse channel ID forwards.

### 5. Help / Manual System
- [ ] Implement a `/manual` or `/faq` command that outputs Telegraph links for Russian and English manuals.
"""

if "Advanced Settings Inline Menus" not in new_text:
    new_text = new_text.replace("## 🏁 Completion Criteria", new_tasks + "\\n## \U0001f3c1 Completion Criteria")

with open("docs/sprints/16_UX_ONBOARDING_KEYBOARDS.md", "w") as f:
    f.write(new_text)

print("Sprint doc updated.")
