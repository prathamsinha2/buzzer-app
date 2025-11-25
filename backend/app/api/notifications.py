from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.models.device import Device
from app.config import settings
import json

router = APIRouter(prefix="/api/notifications", tags=["notifications"])

class SubscriptionRequest(BaseModel):
    device_id: str
    subscription: dict

@router.get("/vapid-public-key")
def get_vapid_public_key(current_user: User = Depends(get_current_user)):
    """
    Return the VAPID public key so the frontend can subscribe to push notifications.
    """
    if not settings.VAPID_PUBLIC_KEY:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="VAPID keys not configured on server"
        )
    return {"publicKey": settings.VAPID_PUBLIC_KEY}

@router.post("/subscribe")
def subscribe(
    request: SubscriptionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Save the push subscription for a specific device.
    """
    device = db.query(Device).filter(Device.device_id == request.device_id).first()
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    
    if device.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to modify this device")

    # Store subscription as JSON string
    device.push_subscription = json.dumps(request.subscription)
    db.commit()
    
    return {"status": "success", "message": "Subscription saved"}
