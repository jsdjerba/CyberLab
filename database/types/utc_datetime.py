from datetime import datetime, timezone
from sqlalchemy import DateTime, TypeDecorator

class UTCDateTime(TypeDecorator):
    """
    Robust SQLAlchemy TypeDecorator ensuring datetime objects 
    are strictly timezone-aware (UTC) in SQLite.
    """
    impl = DateTime
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        if value.tzinfo is None:
            value = value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc)

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc)