from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime

from app.db.base_class import Base
from app.core.security import get_password_hash, verify_password

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    role = Column(String(20), nullable=False, default="agent")  # admin, agent
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    team_memberships = relationship("TeamMember", back_populates="user")
    calls = relationship("Call", back_populates="agent")
    
    def verify_password(self, password: str) -> bool:
        return verify_password(password, self.hashed_password)
    
    def set_password(self, password: str):
        self.hashed_password = get_password_hash(password)
    
    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"