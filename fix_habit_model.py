import re

with open("src/db/models.py", "r") as f:
    text = f.read()

replacement = """class Habit(Base):
    __tablename__ = "habits"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    title: Mapped[str] = mapped_column(String)
    status: Mapped[str] = mapped_column(String, default="active")"""

text = re.sub(r'class Habit\(Base\):\n    __tablename__ = "habits"\n    \n    id: Mapped\[int\] = mapped_column\(primary_key=True\)\n    user_id: Mapped\[int\] = mapped_column\(ForeignKey\("users\.id"\), index=True\)\n    title: Mapped\[str\] = mapped_column\(String\)', replacement, text)

with open("src/db/models.py", "w") as f:
    f.write(text)

