from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_active_user
from app.models.user import User
from app.models.campaign import Campaign

router = APIRouter()

@router.get("/")
async def get_campaigns(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get campaigns"""
    campaigns = db.query(Campaign).offset(skip).limit(limit).all()
    return campaigns

@router.get("/{campaign_id}")
async def get_campaign(
    campaign_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get campaign details"""
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    
    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found"
        )
    
    return campaign