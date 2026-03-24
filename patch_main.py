import re

with open('src/main.py', 'r') as f:
    content = f.read()

import_statement = "from src.admin_dashboard import dashboard_handler\n"
if "from src.admin_dashboard" not in content:
    content = content.replace("from src.bot import routers\n", "from src.bot import routers\n" + import_statement)

route_registration = "\n        app.router.add_get('/admin/dashboard', dashboard_handler)"
if "/admin/dashboard" not in content:
    content = content.replace("setup_application(app, dp, bot=bot)\n", "setup_application(app, dp, bot=bot)\n" + route_registration)

with open('src/main.py', 'w') as f:
    f.write(content)
