"""
Keyboards specifically for Projects, Quests and Tasks CRUD operations.

@Architecture-Map: [UI-KEY-ENT]
@Docs: docs/reference/07_ARCHITECTURE_MAP.md
"""
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from src.bot.texts import PROJECT_EMOJIS

def get_entities_main_keyboard() -> InlineKeyboardMarkup:
    kb = [
        [
            InlineKeyboardButton(text="📁 Manage Projects", callback_data="ui_projects_list")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)



def get_projects_tree_keyboard(all_projects, page=0, toggled_ids=None) -> InlineKeyboardMarkup:
    """Builds a tree-like accordion list of projects."""
    if toggled_ids is None:
        toggled_ids = set()
        
    kb = []
    
    from collections import defaultdict
    children_map = defaultdict(list)
    for p in all_projects:
        children_map[p.parent_id].append(p)
        
    for k in children_map:
        children_map[k].sort(key=lambda p: (0 if p.title.startswith("Project 0") else 1, p.title))
        
    # Flatten the tree
    flat_list = []
    
    def walk(parent_id, depth):
        for p in children_map[parent_id]:
            has_children = len(children_map[p.id]) > 0
            is_expanded = p.id in toggled_ids
            flat_list.append((p, depth, has_children, is_expanded))
            
            if is_expanded and has_children:
                flat_list.append((p, depth + 1, False, False, True)) # special "Manage" node
                walk(p.id, depth + 1)
                
    walk(None, 0)
    
    items_per_page = 15 # more items since it's a tree
    total_pages = max(1, (len(flat_list) + items_per_page - 1) // items_per_page)
    page = max(0, min(page, total_pages - 1))
    
    start = page * items_per_page
    end = start + items_per_page
    
    EMOJIS = PROJECT_EMOJIS
    
    def get_emoji(p):
        if p.title.startswith("Project 0"):
            return "🗂️"
        # If the user put an emoji as the first character, don't generate a random one.
        if p.title and ord(p.title[0]) > 0x2000 and not p.title[0].isspace():
            return "" # The title already has an emoji!
        return EMOJIS[p.id % len(EMOJIS)] + " "

    for item in flat_list[start:end]:
        if len(item) == 5:
            # Special manage node
            p, depth, _, _, _ = item
            prefix = "  " * depth + "└ ⚙️ Open "
            text = f"{prefix}{p.title}"
            kb.append([InlineKeyboardButton(text=text, callback_data=f"ui_proj_{p.id}")])
            continue
            
        p, depth, has_children, is_expanded = item
        
        emoji = get_emoji(p)
        
        # Calculate prefix
        if depth == 0:
            prefix = f"{emoji}"
        else:
            prefix = "  " * depth + f"└ {emoji}"
            
        tree_indicator = ""
        if has_children:
            tree_indicator = " ▾" if is_expanded else " ▸"
            
        text = f"{prefix}[{p.id}] {p.title}{tree_indicator}"
        # Determine callback
        if has_children:
            # Toggle logic
            new_toggles = set(toggled_ids)
            if is_expanded:
                new_toggles.remove(p.id)
            else:
                new_toggles.add(p.id)
            t_str = ".".join(map(str, new_toggles))
            cb_data = f"ui_prjl_{page}_{t_str}"
            if len(cb_data) > 64: # fallback if too large (rare)
                cb_data = f"ui_proj_{p.id}"
        else:
            cb_data = f"ui_proj_{p.id}"
            
        kb.append([InlineKeyboardButton(text=text, callback_data=cb_data)])
        
    # Navigation
    if total_pages > 1:
        nav = []
        t_str = ".".join(map(str, toggled_ids))
        if page > 0:
            nav.append(InlineKeyboardButton(text="⬅️", callback_data=f"ui_prjl_{page-1}_{t_str}"))
        nav.append(InlineKeyboardButton(text=f"{page+1}/{total_pages}", callback_data="ignore"))
        if page < total_pages - 1:
            nav.append(InlineKeyboardButton(text="➡️", callback_data=f"ui_prjl_{page+1}_{t_str}"))
        kb.append(nav)
        
    kb.append([InlineKeyboardButton(text="➕ New Project", callback_data="ui_proj_new")])
    kb.append([InlineKeyboardButton(text="🗄️ Archive", callback_data="ui_proj_archlist")])
    kb.append([InlineKeyboardButton(text="🔙 Back", callback_data="ui_entities_menu")])
    
    return InlineKeyboardMarkup(inline_keyboard=kb)


def get_habits_list_keyboard(habits) -> InlineKeyboardMarkup:
    kb = []
    for h in habits:
        kb.append([InlineKeyboardButton(text=f"🎯 {h.title}", callback_data=f"ui_hab_{h.id}")])
    kb.append([InlineKeyboardButton(text="➕ New", callback_data="ui_hab_new")])
    kb.append([InlineKeyboardButton(text="🔙 Back", callback_data="ui_entities_menu")])
    return InlineKeyboardMarkup(inline_keyboard=kb)


def get_project_view_keyboard(proj_id, status="active", sub_count=0, parent_id=None) -> InlineKeyboardMarkup:
    if status == "archived":
        kb = [
            [
                InlineKeyboardButton(text="🔄 Restore", callback_data=f"ui_proj_unarch_{proj_id}"),
                InlineKeyboardButton(text="🗑 Delete", callback_data=f"ui_proj_delete_{proj_id}")
            ],
            [
                InlineKeyboardButton(text="🔙 Back", callback_data="ui_proj_archlist")
            ]
        ]
        return InlineKeyboardMarkup(inline_keyboard=kb)
        
    kb = [
        [
            InlineKeyboardButton(text="📋 Manage Tasks", callback_data=f"ui_proj_tasks_{proj_id}")
        ],
        [
            InlineKeyboardButton(text="✏️ Edit Target", callback_data=f"ui_proj_edit_{proj_id}"),
            InlineKeyboardButton(text="📊 Add Progress", callback_data=f"ui_proj_add_{proj_id}")
        ],
        [
            InlineKeyboardButton(text="🔥 Edit Daily Target", callback_data=f"ui_proj_editdaily_{proj_id}")
        ],
        [
            InlineKeyboardButton(text="🧹 Reset Daily Progress", callback_data=f"ui_proj_resetdaily_{proj_id}")
        ],
        [
            InlineKeyboardButton(text="�📦 Archive", callback_data=f"ui_proj_arch_{proj_id}"),
            InlineKeyboardButton(text="🗑 Delete", callback_data=f"ui_proj_delete_{proj_id}")
        ],
        [
            InlineKeyboardButton(text="🔙 Back", callback_data="ui_projects_list")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)


def get_habit_view_keyboard(hab_id) -> InlineKeyboardMarkup:
    kb = [
        [
            InlineKeyboardButton(text="✏️ Edit Target", callback_data=f"ui_hab_edit_{hab_id}"),
            InlineKeyboardButton(text="➕ Add Progress", callback_data=f"ui_hab_add_{hab_id}")
        ],
        [
            InlineKeyboardButton(text="⚙️ Periodicity", callback_data=f"ui_hab_period_{hab_id}"),
            InlineKeyboardButton(text="⏱️ Nudge Days", callback_data=f"ui_hab_nudge_{hab_id}")
        ],
        [
            InlineKeyboardButton(text="🗑 Delete/Archive", callback_data=f"ui_hab_arch_{hab_id}")
        ],
        [
            InlineKeyboardButton(text="🔙 Back", callback_data="ui_habits_list")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)

