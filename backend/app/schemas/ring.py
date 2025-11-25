from pydantic import BaseModel
from datetime import datetime


class RingInitiate(BaseModel):
    """Schema for initiating a ring."""
    target_device_id: int
    duration_seconds: int | None = None  # None for continuous


class RingResponse(BaseModel):
    """Schema for ring session response."""
    id: int
    target_device_id: int
    status: str
    duration_seconds: int | None
    started_at: datetime
    stopped_at: datetime | None = None

    class Config:
        from_attributes = True
