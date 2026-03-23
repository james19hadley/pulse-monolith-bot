import sys
import re

with open('src/bot/handlers.py', 'r') as f:
    content = f.read()

# For settings
settings_pattern = r"""msg\s*=\s*"⚙️ \*\*Current Settings\*\*\\n\\n"\s*for key, meta in USER_SETTINGS_REGISTRY\.items\(\):\s*val = getattr\(user, meta\['db_column'\]\)\s*if val is None:\s*val = meta\['default'\]\s*msg \+= f"\*\{meta\['name'\]\}\*:\\n`\{val\}` \(\{meta\['description'\]\}\)\\nChange: `/settings \{key\} <value>`\\n\\n"\s*await message\.answer\(msg,\s*parse_mode="Markdown"\)"""

new_settings_block = """settings_list = []
            for key, meta in USER_SETTINGS_REGISTRY.items():
                val = getattr(user, meta['db_column'])
                if val is None: val = meta['default']
                settings_list.append({'key': key, 'name': meta['name'], 'val': val, 'desc': meta['description']})
                
            await message.answer(settings_list_message(settings_list), parse_mode="Markdown")"""

content = re.sub(settings_pattern, new_settings_block, content, flags=re.MULTILINE)

# For stats
stats_pattern = r"""cost = \(prompt_total / 1000000\.0\) \* 0\.075 \+ \(comp_total / 1000000\.0\) \* 0\.30\s*await message\.answer\([^)]+\)"""
new_stats_block = """cost = (prompt_total / 1000000.0) * 0.075 + (comp_total / 1000000.0) * 0.30
        
        await message.answer(
            stats_message(prompt_total, comp_total, cost),
            parse_mode="Markdown"
        )"""

content = re.sub(stats_pattern, new_stats_block, content, flags=re.MULTILINE)

with open('src/bot/handlers.py', 'w') as f:
    f.write(content)
