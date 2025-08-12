from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime
from app.schemas.user import User

class TeamCreate(BaseModel):
    name: str
    description: Optional[str] = None

class TeamMemberAdd(BaseModel):
    user_id: int
    role: str = "member"

class TeamMemberResponse(BaseModel):
    id: int
    team_id: int
    user_id: int
    role: str
    joined_at: datetime
    user: Optional[User] = None
    
    class Config:
        from_attributes = True

class TeamResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True