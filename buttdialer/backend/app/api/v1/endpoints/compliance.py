from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from io import StringIO
import csv
from datetime import time

from app.api.deps import get_db, get_current_active_user, get_current_admin_user
from app.models.user import User
from app.models.contact import DNCList
from app.schemas.compliance import DNCAdd, DNCResponse, TCPASettings

router = APIRouter()

@router.post("/dnc", response_model=DNCResponse)
async def add_to_dnc(
    dnc_data: DNCAdd,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Add number to Do Not Call list"""
    # Check if already exists
    existing = db.query(DNCList).filter(
        DNCList.phone_number == dnc_data.phone_number
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Number already in DNC list"
        )
    
    dnc_entry = DNCList(
        phone_number=dnc_data.phone_number,
        reason=dnc_data.reason,
        added_by_id=current_user.id
    )
    
    db.add(dnc_entry)
    db.commit()
    db.refresh(dnc_entry)
    
    return dnc_entry

@router.post("/dnc/upload")
async def upload_dnc_list(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Upload DNC list from CSV file (admin only)"""
    if not file.filename.endswith('.csv'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be a CSV"
        )
    
    try:
        content = await file.read()
        csv_content = StringIO(content.decode('utf-8'))
        csv_reader = csv.DictReader(csv_content)
        
        added_count = 0
        skipped_count = 0
        
        for row in csv_reader:
            phone_number = row.get('phone_number', '').strip()
            reason = row.get('reason', 'Uploaded from CSV').strip()
            
            if not phone_number:
                continue
            
            # Check if already exists
            existing = db.query(DNCList).filter(
                DNCList.phone_number == phone_number
            ).first()
            
            if existing:
                skipped_count += 1
                continue
            
            dnc_entry = DNCList(
                phone_number=phone_number,
                reason=reason,
                added_by_id=current_user.id
            )
            
            db.add(dnc_entry)
            added_count += 1
        
        db.commit()
        
        return {
            "message": f"DNC upload completed",
            "added": added_count,
            "skipped": skipped_count
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing file: {str(e)}"
        )

@router.get("/dnc", response_model=List[DNCResponse])
async def get_dnc_list(
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get DNC list with optional search"""
    query = db.query(DNCList)
    
    if search:
        query = query.filter(DNCList.phone_number.contains(search))
    
    dnc_entries = query.offset(skip).limit(limit).all()
    return dnc_entries

@router.delete("/dnc/{dnc_id}")
async def remove_from_dnc(
    dnc_id: int,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Remove number from DNC list (admin only)"""
    dnc_entry = db.query(DNCList).filter(DNCList.id == dnc_id).first()
    
    if not dnc_entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="DNC entry not found"
        )
    
    db.delete(dnc_entry)
    db.commit()
    
    return {"message": "Number removed from DNC list"}

@router.get("/dnc/check/{phone_number}")
async def check_dnc_status(
    phone_number: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Check if number is on DNC list"""
    dnc_entry = db.query(DNCList).filter(
        DNCList.phone_number == phone_number
    ).first()
    
    return {
        "phone_number": phone_number,
        "is_dnc": bool(dnc_entry),
        "reason": dnc_entry.reason if dnc_entry else None,
        "added_at": dnc_entry.added_at.isoformat() if dnc_entry else None
    }

@router.get("/tcpa/calling-hours")
async def get_tcpa_calling_hours():
    """Get TCPA compliant calling hours"""
    return {
        "start_time": "08:00",  # 8 AM local time
        "end_time": "21:00",    # 9 PM local time
        "timezone_note": "Times should be in recipient's local timezone",
        "days": ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday"],
        "restricted_days": ["sunday"],  # Some states restrict Sunday calling
        "federal_holidays_restricted": True
    }

@router.post("/tcpa/validate-calling-time")
async def validate_calling_time(
    phone_number: str,
    current_time: str,  # Format: "HH:MM"
    timezone: str = "America/New_York",
    current_user: User = Depends(get_current_active_user)
):
    """Validate if it's appropriate time to call based on TCPA"""
    try:
        call_time = time.fromisoformat(current_time)
        
        # TCPA allows calls between 8 AM and 9 PM in recipient's timezone
        start_time = time(8, 0)   # 8:00 AM
        end_time = time(21, 0)    # 9:00 PM
        
        is_valid_time = start_time <= call_time <= end_time
        
        return {
            "phone_number": phone_number,
            "call_time": current_time,
            "timezone": timezone,
            "is_valid": is_valid_time,
            "reason": "Within TCPA allowed hours (8 AM - 9 PM)" if is_valid_time else "Outside TCPA allowed hours"
        }
        
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid time format. Use HH:MM"
        )