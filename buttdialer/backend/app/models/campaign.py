from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Time, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime

from app.db.base_class import Base

class Campaign(Base):
    __tablename__ = "campaigns"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=False)
    status = Column(String(20), nullable=False, default="draft")  # draft, active, paused, completed
    call_script = Column(Text)
    tts_message = Column(Text)
    tts_voice_id = Column(String(50))
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    call_hours_start = Column(Time)  # TCPA compliance
    call_hours_end = Column(Time)    # TCPA compliance
    max_attempts = Column(Integer, default=3)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    team = relationship("Team", back_populates="campaigns")
    calls = relationship("Call", back_populates="campaign")
    campaign_calls = relationship("CampaignCall", back_populates="campaign")

class CampaignCall(Base):
    __tablename__ = "campaign_calls"
    
    id = Column(Integer, primary_key=True, index=True)
    campaign_id = Column(Integer, ForeignKey("campaigns.id"), nullable=False)
    contact_id = Column(Integer, ForeignKey("contacts.id"), nullable=False)
    status = Column(String(20), nullable=False, default="pending")  # pending, scheduled, completed, failed
    attempts = Column(Integer, default=0)
    last_attempt_at = Column(DateTime)
    scheduled_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    campaign = relationship("Campaign", back_populates="campaign_calls")
    contact = relationship("Contact", back_populates="campaign_calls")
    
    __table_args__ = (
        UniqueConstraint('campaign_id', 'contact_id', name='_campaign_contact_uc'),
    )