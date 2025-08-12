from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Form, Request
from fastapi.responses import Response
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from datetime import datetime, date

from app.api.deps import get_db, get_current_active_user
from app.models.user import User
from app.models.call import Call
from app.models.contact import Contact, DNCList
from app.services.twilio_service import twilio_service
from app.schemas.call import CallCreate, CallResponse, CallUpdate, CallStats

router = APIRouter()

@router.post("/outbound", response_model=CallResponse)
async def make_outbound_call(
    call_data: CallCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Make an outbound call"""
    # Check DNC list
    dnc_number = db.query(DNCList).filter(DNCList.phone_number == call_data.to_number).first()
    if dnc_number:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Number is on Do Not Call list"
        )
    
    # Get or create contact
    contact = db.query(Contact).filter(Contact.phone_number == call_data.to_number).first()
    if not contact:
        contact = Contact(phone_number=call_data.to_number)
        db.add(contact)
        db.commit()
        db.refresh(contact)
    
    # Make call via Twilio
    result = await twilio_service.make_outbound_call(
        to_number=call_data.to_number,
        agent_id=current_user.id,
        campaign_id=call_data.campaign_id,
        contact_id=contact.id
    )
    
    if not result['success']:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=result.get('error', 'Failed to initiate call')
        )
    
    # Get the created call record
    call = db.query(Call).filter(Call.id == result['call_id']).first()
    return call

@router.post("/parallel", response_model=List[CallResponse])
async def make_parallel_calls(
    phone_numbers: List[str],
    campaign_id: Optional[int] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Make multiple parallel calls (max 3)"""
    if len(phone_numbers) > 3:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Maximum 3 parallel calls allowed"
        )
    
    # Filter out DNC numbers
    dnc_numbers = db.query(DNCList.phone_number).filter(
        DNCList.phone_number.in_(phone_numbers)
    ).all()
    dnc_set = {num[0] for num in dnc_numbers}
    
    valid_numbers = [num for num in phone_numbers if num not in dnc_set]
    
    if not valid_numbers:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="All numbers are on Do Not Call list"
        )
    
    # Make parallel calls
    results = await twilio_service.make_parallel_calls(
        valid_numbers,
        current_user.id,
        campaign_id
    )
    
    # Get call records
    call_ids = [r['call_id'] for r in results if r['success']]
    calls = db.query(Call).filter(Call.id.in_(call_ids)).all()
    
    return calls

@router.get("/token")
async def get_webrtc_token(
    current_user: User = Depends(get_current_active_user)
):
    """Get WebRTC access token for softphone"""
    identity = f"agent-{current_user.id}"
    token = twilio_service.generate_access_token(identity)
    
    return {
        "token": token,
        "identity": identity
    }

@router.post("/voice-webhook")
async def voice_webhook(request: Request):
    """Handle incoming call or call connection"""
    form_data = await request.form()
    twiml_response = twilio_service.generate_ivr_response()
    return Response(content=twiml_response, media_type="application/xml")

@router.post("/ivr-handler")
async def ivr_handler(request: Request):
    """Handle IVR digit input"""
    form_data = await request.form()
    digits = form_data.get('Digits')
    twiml_response = twilio_service.generate_ivr_response(digits)
    return Response(content=twiml_response, media_type="application/xml")

@router.post("/status-webhook")
async def status_webhook(
    CallSid: str = Form(...),
    CallStatus: str = Form(...),
    db: Session = Depends(get_db)
):
    """Handle call status updates from Twilio"""
    await twilio_service.update_call_status(CallSid, CallStatus)
    return {"status": "ok"}

@router.post("/recording-webhook")
async def recording_webhook(
    CallSid: str = Form(...),
    RecordingSid: str = Form(...),
    RecordingUrl: str = Form(...),
    db: Session = Depends(get_db)
):
    """Handle recording completion from Twilio"""
    await twilio_service.save_recording(CallSid, RecordingSid, RecordingUrl)
    return {"status": "ok"}

@router.get("/", response_model=List[CallResponse])
async def get_calls(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get call history with filters"""
    query = db.query(Call)
    
    # Filter by user role
    if current_user.role != "admin":
        query = query.filter(Call.agent_id == current_user.id)
    
    # Apply filters
    if status:
        query = query.filter(Call.status == status)
    
    if date_from:
        query = query.filter(Call.started_at >= date_from)
    
    if date_to:
        query = query.filter(Call.started_at <= date_to)
    
    calls = query.offset(skip).limit(limit).all()
    return calls

@router.get("/stats", response_model=CallStats)
async def get_call_stats(
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get call statistics"""
    query = db.query(Call)
    
    if current_user.role != "admin":
        query = query.filter(Call.agent_id == current_user.id)
    
    if date_from:
        query = query.filter(Call.started_at >= date_from)
    
    if date_to:
        query = query.filter(Call.started_at <= date_to)
    
    total_calls = query.count()
    answered_calls = query.filter(Call.status == 'completed').count()
    total_duration = sum(call.duration or 0 for call in query.all())
    
    connect_rate = (answered_calls / total_calls * 100) if total_calls > 0 else 0
    avg_duration = (total_duration / answered_calls) if answered_calls > 0 else 0
    
    return {
        "total_calls": total_calls,
        "answered_calls": answered_calls,
        "connect_rate": connect_rate,
        "total_duration": total_duration,
        "average_duration": avg_duration
    }

@router.put("/{call_id}", response_model=CallResponse)
async def update_call(
    call_id: int,
    call_update: CallUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update call disposition and notes"""
    call = db.query(Call).filter(Call.id == call_id).first()
    
    if not call:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Call not found"
        )
    
    # Check permission
    if current_user.role != "admin" and call.agent_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this call"
        )
    
    if call_update.disposition:
        call.disposition = call_update.disposition
    if call_update.notes:
        call.notes = call_update.notes
    
    db.commit()
    db.refresh(call)
    
    return call

@router.post("/{call_id}/end")
async def end_call(
    call_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """End an active call"""
    call = db.query(Call).filter(Call.id == call_id).first()
    
    if not call:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Call not found"
        )
    
    # Check permission
    if current_user.role != "admin" and call.agent_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to end this call"
        )
    
    success = twilio_service.end_call(call.twilio_call_sid)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to end call"
        )
    
    return {"status": "call ended"}