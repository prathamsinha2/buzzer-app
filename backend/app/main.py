from fastapi import FastAPI, WebSocket, WebSocketDisconnect, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
import json
import logging

logger = logging.getLogger(__name__)

from app.database import Base, engine
from app.config import settings
from app.api import auth, groups, devices, rings, notifications

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title=settings.APP_NAME, debug=settings.DEBUG)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
app.include_router(auth.router)
app.include_router(groups.router)
app.include_router(devices.router)
app.include_router(rings.router)
app.include_router(notifications.router)


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "ok"}


@app.websocket("/ws/{device_id}")
async def websocket_endpoint(websocket: WebSocket, device_id: str, token: str):
    """WebSocket endpoint for real-time device communication."""
    from app.utils.security import verify_token
    from app.database import SessionLocal
    from app.models.user import User
    from app.models.device import Device
    from app.models.group import GroupMember
    from app.websocket.manager import manager
    from datetime import datetime

    # Verify token
    payload = verify_token(token)
    if not payload:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Invalid token")
        return

    user_id = payload.get("sub")
    if not user_id:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Invalid token")
        return

    # Get user from database
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == int(user_id)).first()
        if not user:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="User not found")
            return

        # Get or create device
        device = db.query(Device).filter(Device.device_id == device_id).first()
        if not device:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Device not found")
            return

        # Get user's groups
        group_memberships = db.query(GroupMember).filter(
            GroupMember.user_id == user.id
        ).all()
        group_ids = {gm.group_id for gm in group_memberships}

        # Register connection
        await manager.connect(websocket, device_id, user.id, group_ids)

        # Update device online status
        device.is_online = True
        device.last_seen = datetime.utcnow()
        db.commit()

        # Broadcast device online status
        await manager.broadcast_device_status(device_id, group_ids, True, device.device_name)

        logger.info(f"Device {device_id} (user {user.id}) WebSocket connected")

        try:
            while True:
                # Receive message from client
                data = await websocket.receive_json()
                msg_type = data.get("type")

                if msg_type == "heartbeat":
                    # Update last seen and respond with pong
                    device.last_seen = datetime.utcnow()
                    db.commit()
                    await websocket.send_json({
                        "type": "pong",
                        "timestamp": datetime.utcnow().isoformat()
                    })

                elif msg_type == "ring_started":
                    # Device confirmed ringing
                    ring_session_id = data.get("ring_session_id")
                    logger.info(f"Device {device_id} started ringing (session {ring_session_id})")
                    # Optionally update ring session status in DB

                elif msg_type == "ring_stopped":
                    # Device stopped ringing (either by duration or manual stop)
                    ring_session_id = data.get("ring_session_id")
                    logger.info(f"Device {device_id} stopped ringing (session {ring_session_id})")
                    # Optionally update ring session status in DB

                elif msg_type == "ring_completed":
                    # Ring duration completed naturally
                    ring_session_id = data.get("ring_session_id")
                    logger.info(f"Device {device_id} ring completed (session {ring_session_id})")

        except WebSocketDisconnect:
            await manager.disconnect(device_id)
            device.is_online = False
            db.commit()
            await manager.broadcast_device_status(device_id, group_ids, False)
            logger.info(f"Device {device_id} WebSocket disconnected")

        except Exception as e:
            logger.error(f"WebSocket error for device {device_id}: {e}")
            await manager.disconnect(device_id)
            device.is_online = False
            db.commit()

    finally:
        db.close()


# Serve static frontend files
frontend_path = os.path.join(os.path.dirname(__file__), "..", "..", "frontend")
if os.path.exists(frontend_path):
    app.mount("/", StaticFiles(directory=frontend_path, html=True), name="frontend")
