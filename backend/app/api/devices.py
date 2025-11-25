from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime
from app.database import get_db
from app.models.user import User
from app.models.device import Device
from app.models.group import GroupMember
from app.schemas.device import DeviceRegister, DeviceResponse
from app.api.deps import get_current_user

router = APIRouter(prefix="/api/devices", tags=["devices"])


@router.post("/register", response_model=DeviceResponse)
def register_device(
    device_data: DeviceRegister,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Register a device for current user."""
    # Check if device already registered
    existing_device = db.query(Device).filter(
        Device.device_id == device_data.device_id
    ).first()
    if existing_device:
        # Update existing device
        existing_device.device_name = device_data.device_name
        existing_device.browser_info = device_data.device_info
        existing_device.last_seen = datetime.utcnow()
        existing_device.is_online = False
        db.commit()
        db.refresh(existing_device)
        return DeviceResponse.from_orm(existing_device)

    # Create new device
    device = Device(
        user_id=current_user.id,
        device_name=device_data.device_name,
        device_id=device_data.device_id,
        browser_info=device_data.device_info,
        is_online=False
    )
    db.add(device)
    db.commit()
    db.refresh(device)

    return DeviceResponse(
        id=device.id,
        user_id=device.user_id,
        device_id=device.device_id,
        device_name=device.device_name,
        device_type=device.device_type,
        user_name=current_user.full_name,
        is_online=device.is_online,
        last_seen=device.last_seen
    )


@router.get("/", response_model=list[DeviceResponse])
def get_devices(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all devices for current user."""
    devices = db.query(Device).filter(Device.user_id == current_user.id).all()
    return [
        DeviceResponse(
            id=d.id,
            user_id=d.user_id,
            device_id=d.device_id,
            device_name=d.device_name,
            device_type=d.device_type,
            user_name=current_user.full_name,
            is_online=d.is_online,
            last_seen=d.last_seen
        )
        for d in devices
    ]


@router.get("/group/{group_id}", response_model=list[DeviceResponse])
def get_group_devices(
    group_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all devices in a group."""
    # Check if user is member of group
    membership = db.query(GroupMember).filter(
        GroupMember.group_id == group_id,
        GroupMember.user_id == current_user.id
    ).first()
    if not membership:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not a member of this group"
        )

    # Get all devices from group members with user info
    results = db.query(Device, User.full_name).join(
        User,
        Device.user_id == User.id
    ).join(
        GroupMember,
        GroupMember.user_id == User.id
    ).filter(
        GroupMember.group_id == group_id
    ).all()

    return [
        DeviceResponse(
            id=d.id,
            user_id=d.user_id,
            device_id=d.device_id,
            device_name=d.device_name,
            device_type=d.device_type,
            user_name=full_name,
            is_online=d.is_online,
            last_seen=d.last_seen
        )
        for d, full_name in results
    ]


@router.delete("/{device_id}")
def delete_device(
    device_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a device."""
    device = db.query(Device).filter(Device.id == device_id).first()
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Device not found"
        )

    # Check ownership
    if device.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot delete another user's device"
        )

    db.delete(device)
    db.commit()

    return {"message": "Device deleted successfully"}
