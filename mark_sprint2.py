with open("docs/sprints/00_SPRINTS_MASTER.md", "r") as f:
    text = f.read()

text += "\n- [x] Settings UX: Add test report inline button\n- [x] Settings UX: Fix attribute exceptions for onboarding and help\n"

with open("docs/sprints/00_SPRINTS_MASTER.md", "w") as f:
    f.write(text)

