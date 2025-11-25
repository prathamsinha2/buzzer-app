from pydantic import BaseModel
from datetime import datetime


class GroupCreate(BaseModel):
    """Schema for creating a group."""
    name: str


class GroupJoin(BaseModel):
    """Schema for joining a group."""
    invite_code: str


class MemberResponse(BaseModel):
    """Schema for group member response."""
    id: int
    email: str
    full_name: str | None
    role: str

    class Config:
        from_attributes = True


class GroupResponse(BaseModel):
    """Schema for group response."""
    id: int
    name: str
    invite_code: str
    owner_id: int
    members: list[MemberResponse] = []

    class Config:
        from_attributes = True


class GroupDetailResponse(GroupResponse):
    """Detailed group response with created date."""
    created_at: datetime
    updated_at: datetime
