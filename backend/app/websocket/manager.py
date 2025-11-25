from fastapi import WebSocket
from typing import Dict, Set
import json
import asyncio
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class ConnectionManager:
    """Manages WebSocket connections and routes messages."""

    def __init__(self):
        # device_id -> WebSocket connection
        self.active_connections: Dict[str, WebSocket] = {}

        # user_id -> Set of device_ids
        self.user_devices: Dict[int, Set[str]] = {}

        # device_id -> user_id mapping
        self.device_users: Dict[str, int] = {}

        # device_id -> group_ids mapping
        self.device_groups: Dict[str, Set[int]] = {}

    async def connect(
        self,
        websocket: WebSocket,
        device_id: str,
        user_id: int,
        group_ids: Set[int] = None
    ):
        """Register a new device connection."""
        await websocket.accept()
        self.active_connections[device_id] = websocket
        self.device_users[device_id] = user_id

        # Track devices per user
        if user_id not in self.user_devices:
            self.user_devices[user_id] = set()
        self.user_devices[user_id].add(device_id)

        # Track groups for device
        if group_ids:
            self.device_groups[device_id] = group_ids
        else:
            self.device_groups[device_id] = set()

        logger.info(f"Device {device_id} (user {user_id}) connected")

    async def disconnect(self, device_id: str):
        """Unregister a device connection."""
        if device_id in self.active_connections:
            del self.active_connections[device_id]

        if device_id in self.device_users:
            user_id = self.device_users[device_id]
            del self.device_users[device_id]

            if user_id in self.user_devices:
                self.user_devices[user_id].discard(device_id)
                if not self.user_devices[user_id]:
                    del self.user_devices[user_id]

        if device_id in self.device_groups:
            del self.device_groups[device_id]

        logger.info(f"Device {device_id} disconnected")

    async def send_to_device(self, device_id: str, message: dict) -> bool:
        """Send a message to a specific device."""
        if device_id in self.active_connections:
            try:
                websocket = self.active_connections[device_id]
                await websocket.send_json(message)
                logger.debug(f"Message sent to device {device_id}")
                return True
            except Exception as e:
                logger.error(f"Error sending message to device {device_id}: {e}")
                # Remove connection if it's broken
                await self.disconnect(device_id)
                return False
        return False

    async def send_to_group_devices(self, group_id: int, message: dict):
        """Send a message to all devices in a group."""
        disconnected = []
        for device_id, groups in self.device_groups.items():
            if group_id in groups:
                success = await self.send_to_device(device_id, message)
                if not success:
                    disconnected.append(device_id)

        # Clean up disconnected devices
        for device_id in disconnected:
            await self.disconnect(device_id)

    async def send_to_user_devices(self, user_id: int, message: dict):
        """Send a message to all devices of a user."""
        if user_id in self.user_devices:
            disconnected = []
            for device_id in self.user_devices[user_id]:
                success = await self.send_to_device(device_id, message)
                if not success:
                    disconnected.append(device_id)

            # Clean up disconnected devices
            for device_id in disconnected:
                await self.disconnect(device_id)

    async def broadcast_device_status(self, device_id: str, group_ids: Set[int], online: bool, device_name: str = None):
        """Broadcast a device's online status to all devices in its groups."""
        message = {
            "type": "device_status_changed",
            "device_id": device_id,
            "online": online,
            "device_name": device_name,
            "timestamp": datetime.utcnow().isoformat()
        }

        for group_id in group_ids:
            await self.send_to_group_devices(group_id, message)

    def get_online_devices_in_group(self, group_id: int) -> list[str]:
        """Get all online devices in a group."""
        online_devices = []
        for device_id, groups in self.device_groups.items():
            if group_id in groups and device_id in self.active_connections:
                online_devices.append(device_id)
        return online_devices

    def is_device_online(self, device_id: str) -> bool:
        """Check if a device is currently online."""
        return device_id in self.active_connections


# Global connection manager instance
manager = ConnectionManager()
