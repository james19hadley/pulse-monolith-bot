with open("src/bot/handlers/core.py", "r") as f:
    text = f.read()

text = text.replace("<code>/start_session</code>", "/start_session")
text = text.replace("<code>/end_session</code>", "/end_session")
text = text.replace("<code>/log &lt;min&gt; [desc]</code>", "/log &lt;min&gt; [desc]")
text = text.replace("<code>/habit &lt;id/name&gt; [val]</code>", "/habit &lt;id/name&gt; [val]")
text = text.replace("<code>/inbox &lt;text&gt;</code>", "/inbox &lt;text&gt;")
text = text.replace("<code>/projects</code>", "/projects")
text = text.replace("<code>/habits</code>", "/habits")
text = text.replace("<code>/new_project &lt;name&gt; | [target_hours]</code>", "/new_project &lt;name&gt; | [target_hours]")
text = text.replace("<code>/new_habit &lt;name&gt;</code>", "/new_habit &lt;name&gt;")
text = text.replace("<code>/settings</code>", "/settings")
text = text.replace("<code>/persona</code>", "/persona")
text = text.replace("<code>/tokens</code>", "/tokens")
text = text.replace("<code>/test_report</code>", "/test_report")
text = text.replace("<code>/add_key &lt;provider&gt; &lt;key&gt; [name]</code>", "/add_key &lt;provider&gt; &lt;key&gt; [name]")
text = text.replace("<code>/my_key</code>", "/my_key")
text = text.replace("<code>/delete_key &lt;name&gt;</code>", "/delete_key &lt;name&gt;")
text = text.replace("<code>/log", "/log")
text = text.replace("</code>", "")

with open("src/bot/handlers/core.py", "w") as f:
    f.write(text)
