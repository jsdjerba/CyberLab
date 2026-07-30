from sqlalchemy import Column, String, DateTime
from infrastructure.database import Base

class AuditEventModel(Base):
    __tablename__ = "security_audit_logs"
    
    event_id = Column(String(50), primary_key=True)
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True)
    action = Column(String(50), nullable=False)
    status = Column(String(20), nullable=False)
    user_id = Column(String(50), nullable=False, index=True)
    details = Column(String(255))
    ip_address = Column(String(50))