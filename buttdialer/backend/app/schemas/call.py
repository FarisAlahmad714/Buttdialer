from typing import Optional
from pydantic import BaseModel
from datetime import datetime

class CallBase(BaseModel):
    to_number: str
    campaign_id: Optional[int] = None

class CallCreate(CallBase):
    pass

class CallUpdate(BaseModel):
    disposition: Optional[str] = None
    notes: Optional[str] = None

class CallResponse(BaseModel):
    id: int
    twilio_call_sid: Optional[str]
    agent_id: int
    contact_id: Optional[int]
    campaign_id: Optional[int]
    direction: str
    from_number: str
    to_number: str
    status: str
    duration: int
    started_at: datetime
    answered_at: Optional[datetime]
    ended_at: Optional[datetime]
    disposition: Optional[str]
    notes: Optional[str]
    
    class Config:
        from_attributes = True

class CallStats(BaseModel):
    total_calls: int
    answered_calls: int
    connect_rate: float
    total_duration: int
    average_duration: float