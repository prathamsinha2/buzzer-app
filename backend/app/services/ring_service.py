from sqlalchemy.orm import Session
from datetime import datetime
from app.models.ring_session import RingSession
from app.models.device import Device
from app.models.group import GroupMember
from app.websocket.manager import manager


async def start_ring_session(
    db: Session,
    group_id: int,
    initiated_by_user_id: int,
    target_device_id: int,
    duration_seconds: int = None
) -> RingSession:
    """Start a ring session and send command via WebSocket."""

    # Get target device
    device = db.query(Device).filter(Device.id == target_device_id).first()
    if not device:
        raise ValueError("Device not found")

    # Create ring session
    ring_session = RingSession(
        group_id=group_id,
        initiated_by=initiated_by_user_id,
        target_device_id=target_device_id,
        duration_seconds=duration_seconds,
        status="initiated"
    )
    db.add(ring_session)
    db.commit()
    db.refresh(ring_session)

    # Send ring command via WebSocket
    message = {
        "type": "ring_command",
        "ring_session_id": ring_session.id,
        "duration": duration_seconds,
        "initiated_by_user_id": initiated_by_user_id,
        "timestamp": datetime.utcnow().isoformat()
    }

    success = await manager.send_to_device(device.device_id, message)

    if success:
        ring_session.status = "ringing"
        db.commit()
    else:
        ring_session.status = "failed"
        db.commit()
        raise ValueError("Failed to send ring command - device may be offline")

    return ring_session


async def stop_ring_session(
    db: Session,
    ring_session_id: int
) -> RingSession:
    """Stop a ring session."""

    ring_session = db.query(RingSession).filter(
        RingSession.id == ring_session_id
    ).first()
    if not ring_session:
        raise ValueError("Ring session not found")

    device = db.query(Device).filter(
        Device.id == ring_session.target_device_id
    ).first()

    # Send stop command
    message = {
        "type": "stop_command",
        "ring_session_id": ring_session_id,
        "timestamp": datetime.utcnow().isoformat()
    }

    await manager.send_to_device(device.device_id, message)

    ring_session.status = "stopped"
    ring_session.stopped_at = datetime.utcnow()
    db.commit()

    return ring_session


def get_ring_session(db: Session, ring_session_id: int) -> RingSession:
    """Get a ring session by ID."""
    return db.query(RingSession).filter(
        RingSession.id == ring_session_id
    ).first()
