with open("docs/sprints/00_SPRINTS_MASTER.md", "r") as f:
    text = f.read()

text = text.replace("| [Sprint 19](19_REPORTING_ENGINE.md) | Reporting Engine & Timezone Accuracy | ⚪ Draft |", "| [Sprint 19](19_REPORTING_ENGINE.md) | Reporting Engine & Timezone Accuracy | 🟢 Completed |")
text = text.replace("| [Sprint 20](20_ENTITY_MANAGEMENT_UI.md) | Entity Management UI (Inline Panels)\n | ⚪ Draft |", "| [Sprint 20](20_ENTITY_MANAGEMENT_UI.md) | Entity Management UI (Inline Panels) | 🟡 Active |")
text = text.replace("| [Sprint 20](20_ENTITY_MANAGEMENT_UI.md) | Entity Management UI (Inline Panels) | ⚪ Draft |", "| [Sprint 20](20_ENTITY_MANAGEMENT_UI.md) | Entity Management UI (Inline Panels) | 🟡 Active |")

with open("docs/sprints/00_SPRINTS_MASTER.md", "w") as f:
    f.write(text)

with open("docs/sprints/19_REPORTING_ENGINE.md", "r") as f:
    text = f.read()

text = text.replace("**Status:** `Active`", "**Status:** `Completed`")

with open("docs/sprints/19_REPORTING_ENGINE.md", "w") as f:
    f.write(text)

with open("docs/sprints/20_ENTITY_MANAGEMENT_UI.md", "r") as f:
    text = f.read()

text = text.replace("**Status:** `Draft`", "**Status:** `Active`")

with open("docs/sprints/20_ENTITY_MANAGEMENT_UI.md", "w") as f:
    f.write(text)

