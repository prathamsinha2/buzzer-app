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
    target_device = db.query(Device).filter(Device.id == target_device_id).first()
    if not target_device:
        raise ValueError("Device not found")

    # Get initiator name
    from app.models.user import User
    initiator = db.query(User).filter(User.id == initiated_by_user_id).first()
    initiator_name = initiator.full_name if initiator else "Someone"

    # Create ring session
    ring_session = RingSession(
        group_id=group_id,
        initiated_by=initiated_by_user_id,
        target_device_id=target_device_id,
        duration_seconds=duration_seconds,
        status="active"
    )
    db.add(ring_session)
    db.commit()
    db.refresh(ring_session)

    # 1. Send WebSocket message (for in-app UI)
    await manager.send_to_device(
        target_device.device_id,
        {
            "type": "ring_command",
            "ring_session_id": ring_session.id,
            "duration": duration_seconds,
            "initiator_name": initiator_name
        }
    )

    # 2. Send Web Push Notification (for background/system)
    if target_device.push_subscription:
        try:
            from pywebpush import webpush, WebPushException
            import json
            from app.config import settings

            subscription_info = json.loads(target_device.push_subscription)
            
            # Only send if keys are configured
            if settings.VAPID_PRIVATE_KEY and settings.VAPID_CLAIMS_EMAIL:
                webpush(
                    subscription_info=subscription_info,
                    data=json.dumps({
                        "title": "BUZZER",
                        "body": f"{initiator_name} is buzzing you!",
                        "icon": "/static/images/icon-192.png",
                        "url": "/dashboard.html"
                    }),
                    vapid_private_key=settings.VAPID_PRIVATE_KEY,
                    vapid_claims={"sub": settings.VAPID_CLAIMS_EMAIL}
                )
                print(f"Push notification sent to device {target_device.device_name}")
        except Exception as e:
            print(f"Failed to send push notification: {str(e)}")

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
