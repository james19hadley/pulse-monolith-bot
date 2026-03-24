from datetime import datetime, time, date
from typing import Optional, Any
from sqlalchemy import (
    String, 
    Integer, 
    DateTime, 
    Time, 
    Date, 
    ForeignKey, 
    JSON, 
    Text
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    telegram_id: Mapped[int] = mapped_column(unique=True, index=True)
    timezone: Mapped[str] = mapped_column(String, default="UTC")
    # Determines when the "day" ends for the Evening Report
    day_cutoff_time: Mapped[time] = mapped_column(Time, default=time(23, 0)) # 23:00 (11 PM) by default
    llm_provider: Mapped[str] = mapped_column(String, default="google")
    api_key_encrypted: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    
    # Persona Engine
    persona_type: Mapped[str] = mapped_column(String, default="monolith") # monolith, tars, friday, alfred, custom
    custom_persona_prompt: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Links to the currently active session (if any)
    active_session_id: Mapped[Optional[int]] = mapped_column(ForeignKey("sessions.id", use_alter=True), nullable=True)
    last_ping_message_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    # Catalyst Settings
    catalyst_threshold_minutes: Mapped[int] = mapped_column(Integer, default=60)
    catalyst_interval_minutes: Mapped[int] = mapped_column(Integer, default=20)
    target_channel_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    report_config: Mapped[Optional[Any]] = mapped_column(JSON, nullable=True)

    @property
    def api_keys(self) -> dict:
        import json
        if not self.api_key_encrypted:
            return {}
        if self.api_key_encrypted.startswith('{'):
            try:
                data = json.loads(self.api_key_encrypted)
                # auto-migrate old formats
                res = {}
                for k, v in data.items():
                    if isinstance(v, str):
                        res[k] = {"provider": k, "key": v}
                    else:
                        res[k] = v
                return res
            except:
                return {}
        return {self.llm_provider: {"provider": self.llm_provider, "key": self.api_key_encrypted}}

    def set_api_keys(self, keys_dict: dict):
        import json
        if not keys_dict:
            self.api_key_encrypted = None
        else:
            self.api_key_encrypted = json.dumps(keys_dict)

class Session(Base):
    __tablename__ = "sessions"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    start_time: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    end_time: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    status: Mapped[str] = mapped_column(String, default="active") # 'active', 'closed', 'force_closed_by_cron'

class Project(Base):
    __tablename__ = "projects"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    title: Mapped[str] = mapped_column(String)
    status: Mapped[str] = mapped_column(String, default="active") # 'active', 'paused', 'completed'
    target_minutes: Mapped[int] = mapped_column(Integer, default=0) # Total estimated effort
    total_minutes_spent: Mapped[int] = mapped_column(Integer, default=0)
    next_action_text: Mapped[Optional[str]] = mapped_column(String, nullable=True) # E.g., "Read pointers chapter"

class Habit(Base):
    __tablename__ = "habits"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    title: Mapped[str] = mapped_column(String)
    target_value: Mapped[int] = mapped_column(Integer, default=1)
    current_value: Mapped[int] = mapped_column(Integer, default=0)
    type: Mapped[str] = mapped_column(String, default="counter") # 'counter' or 'boolean'
    last_reset_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

class TimeLog(Base):
    """The Ledger: Tracks actual focused work blocks"""
    __tablename__ = "time_logs"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    session_id: Mapped[Optional[int]] = mapped_column(ForeignKey("sessions.id"), nullable=True)
    project_id: Mapped[Optional[int]] = mapped_column(ForeignKey("projects.id"), nullable=True)
    duration_minutes: Mapped[int] = mapped_column(Integer)
    description: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

class ActionLog(Base):
    """The Undo Engine: Records state changes before and after an AI action"""
    __tablename__ = "action_logs"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    tool_name: Mapped[str] = mapped_column(String)
    previous_state_json: Mapped[Any] = mapped_column(JSON)
    new_state_json: Mapped[Any] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

class Inbox(Base):
    """Brain Dump for the user"""
    __tablename__ = "inbox"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    raw_text: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String, default="pending") # 'pending', 'cleared'

class TokenUsage(Base):
    """FinOps: Tracks AI API Token Usage"""
    __tablename__ = "token_usage"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    prompt_tokens: Mapped[int] = mapped_column(Integer, default=0)
    completion_tokens: Mapped[int] = mapped_column(Integer, default=0)
    total_tokens: Mapped[int] = mapped_column(Integer, default=0)
    model_name: Mapped[str] = mapped_column(String)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
