with open("docs/sprints/00_SPRINTS_MASTER.md", "r") as f:
    text = f.read()

text = text.replace('- [ ] Migrate "Repeat interval" to "Ping Interval"', '- [x] Migrate "Repeat interval" to "Ping Interval"')
text = text.replace('- [ ] Personas: Instruct AI not to wrap slash commands in backticks so they are clickable', '- [x] Personas: Instruct AI not to wrap slash commands in backticks so they are clickable')
text = text.replace('- [ ] Intent: `LOG_HABIT` - Parse natural language, match to existing habit, or offer creation via inline keyboard.', '- [x] Intent: `LOG_HABIT` - Parse natural language, match to existing habit, or offer creation via inline keyboard.')
text = text.replace('- [ ] Token Stats: Add daily token usage in addition to total in `/tokens`', '- [x] Token Stats: Add daily token usage in addition to total in `/tokens`')
text = text.replace('- [ ] Undo Support: Provide Inline [Undo] buttons on logged actions', '- [x] Undo Support: Provide Inline [Undo] buttons on logged actions')

with open("docs/sprints/00_SPRINTS_MASTER.md", "w") as f:
    f.write(text)
