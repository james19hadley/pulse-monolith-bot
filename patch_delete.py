import os
import re

# Patch providers.py
with open("src/ai/providers.py", "r") as f:
    content = f.read()

content = content.replace(
    'entity_name_or_id: str = Field(description="The name or ID of the existing entity to edit")',
    'action: str = Field(description="Strictly \'edit\' or \'delete\'", default="edit")\n    entity_name_or_id: str = Field(description="The name or ID of the existing entity to edit or delete")'
)

with open("src/ai/providers.py", "w") as f:
    f.write(content)


# Patch intent_entities.py
with open("src/bot/handlers/intents/intent_entities.py", "r") as f:
    content = f.read()

# We'll use a safer patch for intent_entities
print("Providers patched.")
