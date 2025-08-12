from typing import Optional
from pydantic import BaseModel
from datetime import datetime, time

class DNCAdd(BaseModel):
    phone_number: str
    reason: str = "Customer request"

class DNCResponse(BaseModel):
    id: int
    phone_number: str
    reason: Optional[str]
    added_by_id: int
    added_at: datetime
    
    class Config:
        from_attributes = True

class TCPASettings(BaseModel):
    calling_hours_start: time
    calling_hours_end: time
    restricted_days: list[str] = ["sunday"]
    timezone: str = "America/New_York"