from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.models.device import Device
from app.models.group import GroupMember
from app.models.ring_session import RingSession
from app.schemas.ring import RingInitiate, RingResponse
from app.api.deps import get_current_user
from app.services.ring_service import start_ring_session, stop_ring_session, get_ring_session

router = APIRouter(prefix="/api/rings", tags=["rings"])


@router.post("/start", response_model=RingResponse)
async def start_ring(
    data: RingInitiate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Start ringing a device."""

    # Get target device
    target_device = db.query(Device).filter(Device.id == data.target_device_id).first()
    if not target_device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Device not found"
        )

    # Find a group where both users are members
    group_member = db.query(GroupMember).filter(
        GroupMember.user_id == current_user.id
    ).first()

    if not group_member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not in any group"
        )

    # Verify target device owner is also in the group
    target_owner_membership = db.query(GroupMember).filter(
        GroupMember.group_id == group_member.group_id,
        GroupMember.user_id == target_device.user_id
    ).first()

    if not target_owner_membership:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Target device owner is not in your group"
        )

    # Can't ring offline devices
    if not target_device.is_online:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Target device is offline"
        )

    try:
        ring_session = await start_ring_session(
            db=db,
            group_id=group_member.group_id,
            initiated_by_user_id=current_user.id,
            target_device_id=data.target_device_id,
            duration_seconds=data.duration_seconds
        )

        return RingResponse(
            id=ring_session.id,
            target_device_id=ring_session.target_device_id,
            status=ring_session.status,
            duration_seconds=ring_session.duration_seconds,
            started_at=ring_session.started_at,
            stopped_at=ring_session.stopped_at
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/{ring_session_id}/stop", response_model=RingResponse)
async def stop_ring(
    ring_session_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Stop ringing a device."""

    ring_session = get_ring_session(db, ring_session_id)
    if not ring_session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ring session not found"
        )

    # Check if user initiated this ring or owns the device being rung
    if (ring_session.initiated_by != current_user.id and
            ring_session.target_device.user_id != current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot stop this ring session"
        )

    try:
        ring_session = await stop_ring_session(db, ring_session_id)

        return RingResponse(
            id=ring_session.id,
            target_device_id=ring_session.target_device_id,
            status=ring_session.status,
            duration_seconds=ring_session.duration_seconds,
            started_at=ring_session.started_at,
            stopped_at=ring_session.stopped_at
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/{ring_session_id}", response_model=RingResponse)
def get_ring(
    ring_session_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a ring session."""

    ring_session = get_ring_session(db, ring_session_id)
    if not ring_session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ring session not found"
        )

    # Check if user has access
    if (ring_session.initiated_by != current_user.id and
            ring_session.target_device.user_id != current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No access to this ring session"
        )

    return RingResponse(
        id=ring_session.id,
        target_device_id=ring_session.target_device_id,
        status=ring_session.status,
        duration_seconds=ring_session.duration_seconds,
        started_at=ring_session.started_at,
        stopped_at=ring_session.stopped_at
    )
