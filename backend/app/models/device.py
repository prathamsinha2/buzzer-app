from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class Device(Base):
    __tablename__ = "devices"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    device_name = Column(String(255), nullable=False)
    device_id = Column(String(255), unique=True, index=True, nullable=False)  # UUID v4 from client
    device_type = Column(String(100), nullable=True)  # iPhone 14, iPad Pro, etc
    browser_info = Column(JSON, nullable=True)  # User agent, browser version, screen size
    last_seen = Column(DateTime, default=datetime.utcnow, nullable=True)
    is_online = Column(Boolean, default=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User", back_populates="devices")
    ring_sessions = relationship("RingSession", back_populates="target_device", cascade="all, delete-orphan")
