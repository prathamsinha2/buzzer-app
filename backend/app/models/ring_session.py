from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class RingSession(Base):
    __tablename__ = "ring_sessions"

    id = Column(Integer, primary_key=True, index=True)
    group_id = Column(Integer, ForeignKey("groups.id"), nullable=False)
    initiated_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    target_device_id = Column(Integer, ForeignKey("devices.id"), nullable=False)
    duration_seconds = Column(Integer, nullable=True)  # NULL for continuous
    status = Column(String(50), default="initiated", nullable=False)  # initiated, ringing, stopped, completed, failed
    started_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    stopped_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)

    # Relationships
    group = relationship("Group", back_populates="ring_sessions")
    initiated_by_user = relationship("User", back_populates="rings_initiated")
    target_device = relationship("Device", back_populates="ring_sessions")
