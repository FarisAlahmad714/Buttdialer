from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_active_user
from app.models.user import User
from app.models.contact import Contact

router = APIRouter()

@router.get("/")
async def get_contacts(
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get contacts with optional search"""
    query = db.query(Contact)
    
    if search:
        query = query.filter(
            Contact.phone_number.contains(search) |
            Contact.first_name.contains(search) |
            Contact.last_name.contains(search) |
            Contact.email.contains(search)
        )
    
    contacts = query.offset(skip).limit(limit).all()
    return contacts

@router.get("/{contact_id}")
async def get_contact(
    contact_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get contact details"""
    contact = db.query(Contact).filter(Contact.id == contact_id).first()
    
    if not contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contact not found"
        )
    
    return contact