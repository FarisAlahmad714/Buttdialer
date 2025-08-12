from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, JSON, Text
from sqlalchemy.orm import relationship
from datetime import datetime

from app.db.base_class import Base

class Contact(Base):
    __tablename__ = "contacts"
    
    id = Column(Integer, primary_key=True, index=True)
    phone_number = Column(String(20), unique=True, nullable=False, index=True)
    first_name = Column(String(50))
    last_name = Column(String(50))
    email = Column(String(120))
    company = Column(String(100))
    hubspot_contact_id = Column(String(50), unique=True)
    tags = Column(JSON)
    custom_fields = Column(JSON)
    is_dnc = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    calls = relationship("Call", back_populates="contact")
    campaign_calls = relationship("CampaignCall", back_populates="contact")

class DNCList(Base):
    __tablename__ = "dnc_lists"
    
    id = Column(Integer, primary_key=True, index=True)
    phone_number = Column(String(20), unique=True, nullable=False, index=True)
    reason = Column(String(100))
    added_by_id = Column(Integer, ForeignKey("users.id"))
    added_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    added_by = relationship("User")