# reporting layer
from sqlalchemy.orm import Session
from src.db.models import User, TimeLog, Project, Inbox
import datetime

class ReportingService:
    @staticmethod
    def generate_daily_report(db: Session, user: User, force_date: str = None, is_auto_cron: bool = False) -> str:
    """
    Calculates progress for projects today and orchestrates report building.
    
    @Architecture-Map: [SRV-REPORT-CALC]
    @Docs: docs/07_ARCHITECTURE_MAP.md
    """
        from src.bot.handlers.utils import generate_daily_report_text
        return generate_daily_report_text(db, user, force_date, is_auto_cron)
