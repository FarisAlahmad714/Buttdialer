from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_active_user
from app.models.user import User
from app.models.contact import Contact
from app.models.call import Call
from app.services.hubspot_service import hubspot_service
from app.schemas.crm import ContactSync, CallLog, DealCreate

router = APIRouter()

@router.post("/sync-contacts")
async def sync_contacts_from_hubspot(
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Sync contacts from HubSpot to local database"""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can sync contacts"
        )
    
    # Run sync in background
    background_tasks.add_task(sync_contacts_task, db)
    
    return {"message": "Contact sync started"}

async def sync_contacts_task(db: Session):
    """Background task to sync contacts"""
    try:
        contacts = await hubspot_service.sync_contacts_to_database(limit=100)
        
        for hubspot_contact in contacts:
            properties = hubspot_contact.get('properties', {})
            
            # Check if contact exists
            phone = properties.get('phone')
            if not phone:
                continue
                
            contact = db.query(Contact).filter(Contact.phone_number == phone).first()
            
            if not contact:
                contact = Contact(
                    phone_number=phone,
                    email=properties.get('email'),
                    first_name=properties.get('firstname'),
                    last_name=properties.get('lastname'),
                    company=properties.get('company'),
                    hubspot_contact_id=hubspot_contact.get('id')
                )
                db.add(contact)
            else:
                # Update existing contact
                contact.email = properties.get('email') or contact.email
                contact.first_name = properties.get('firstname') or contact.first_name
                contact.last_name = properties.get('lastname') or contact.last_name
                contact.company = properties.get('company') or contact.company
                contact.hubspot_contact_id = hubspot_contact.get('id')
            
        db.commit()
        
    except Exception as e:
        logger.error(f"Error in sync_contacts_task: {str(e)}")

@router.post("/log-call/{call_id}")
async def log_call_to_hubspot(
    call_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Log a completed call to HubSpot"""
    call = db.query(Call).filter(Call.id == call_id).first()
    
    if not call:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Call not found"
        )
    
    if not call.contact or not call.contact.hubspot_contact_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Call has no associated HubSpot contact"
        )
    
    # Log to HubSpot
    result = await hubspot_service.log_call_activity(
        contact_id=call.contact.hubspot_contact_id,
        call_duration=call.duration or 0,
        call_notes=call.notes or "",
        call_disposition=call.disposition or "completed",
        call_time=call.started_at
    )
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to log call to HubSpot"
        )
    
    return {"message": "Call logged to HubSpot", "hubspot_call_id": result.get('id')}

@router.post("/contacts")
async def create_or_update_contact(
    contact_data: ContactSync,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create or update contact in both local DB and HubSpot"""
    # Create/update in HubSpot
    hubspot_contact = await hubspot_service.create_or_update_contact(
        email=contact_data.email,
        phone=contact_data.phone,
        first_name=contact_data.first_name,
        last_name=contact_data.last_name,
        company=contact_data.company
    )
    
    if not hubspot_contact:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create/update contact in HubSpot"
        )
    
    # Create/update in local DB
    contact = db.query(Contact).filter(Contact.phone_number == contact_data.phone).first()
    
    if not contact:
        contact = Contact(
            phone_number=contact_data.phone,
            email=contact_data.email,
            first_name=contact_data.first_name,
            last_name=contact_data.last_name,
            company=contact_data.company,
            hubspot_contact_id=hubspot_contact.get('id')
        )
        db.add(contact)
    else:
        contact.email = contact_data.email or contact.email
        contact.first_name = contact_data.first_name or contact.first_name
        contact.last_name = contact_data.last_name or contact.last_name
        contact.company = contact_data.company or contact.company
        contact.hubspot_contact_id = hubspot_contact.get('id')
    
    db.commit()
    db.refresh(contact)
    
    return contact

@router.get("/contacts/search")
async def search_contacts(
    query: str,
    current_user: User = Depends(get_current_active_user)
):
    """Search contacts in HubSpot"""
    results = await hubspot_service.search_contacts(query)
    
    if not results:
        return {"results": []}
    
    return results

@router.post("/deals")
async def create_deal(
    deal_data: DealCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a deal in HubSpot"""
    # Get contact
    contact = db.query(Contact).filter(Contact.id == deal_data.contact_id).first()
    
    if not contact or not contact.hubspot_contact_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Contact not found or not synced with HubSpot"
        )
    
    # Create deal in HubSpot
    deal = await hubspot_service.create_deal(
        deal_name=deal_data.name,
        amount=deal_data.amount,
        contact_id=contact.hubspot_contact_id,
        pipeline_stage=deal_data.stage
    )
    
    if not deal:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create deal in HubSpot"
        )
    
    return {"message": "Deal created", "hubspot_deal_id": deal.get('id')}