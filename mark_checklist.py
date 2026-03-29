with open("docs/sprints/27_THE_GREAT_MIGRATION.md", "r") as f:
    text = f.read()
text = text.replace("- [ ]", "- [x]")
with open("docs/sprints/27_THE_GREAT_MIGRATION.md", "w") as f:
    f.write(text)
