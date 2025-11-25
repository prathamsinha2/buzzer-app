from pydantic import BaseModel
from datetime import datetime


class DeviceRegister(BaseModel):
    """Schema for registering a device."""
    device_id: str  # UUID v4 from client
    device_name: str
    device_info: dict | None = None


class DeviceResponse(BaseModel):
    """Schema for device response."""
    id: int
    device_id: str
    device_name: str
    device_type: str | None
    is_online: bool
    last_seen: datetime | None

    class Config:
        from_attributes = True


class DeviceDetailResponse(DeviceResponse):
    """Detailed device response."""
    browser_info: dict | None
    created_at: datetime
    updated_at: datetime
