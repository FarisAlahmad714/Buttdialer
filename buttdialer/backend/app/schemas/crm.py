from typing import Optional
from pydantic import BaseModel

class ContactSync(BaseModel):
    email: Optional[str] = None
    phone: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    company: Optional[str] = None

class CallLog(BaseModel):
    call_id: int

class DealCreate(BaseModel):
    name: str
    amount: float
    contact_id: int
    stage: str = "appointmentscheduled"