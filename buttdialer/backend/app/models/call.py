from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime

from app.db.base_class import Base

class Call(Base):
    __tablename__ = "calls"
    
    id = Column(Integer, primary_key=True, index=True)
    twilio_call_sid = Column(String(100), unique=True, index=True)
    agent_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    contact_id = Column(Integer, ForeignKey("contacts.id"))
    campaign_id = Column(Integer, ForeignKey("campaigns.id"))
    direction = Column(String(20), nullable=False)  # inbound, outbound
    from_number = Column(String(20), nullable=False)
    to_number = Column(String(20), nullable=False)
    status = Column(String(20), nullable=False, default="initiated")
    duration = Column(Integer, default=0)  # seconds
    started_at = Column(DateTime, default=datetime.utcnow)
    answered_at = Column(DateTime)
    ended_at = Column(DateTime)
    notes = Column(Text)
    disposition = Column(String(50))  # interested, not-interested, callback, voicemail
    
    # Relationships
    agent = relationship("User", back_populates="calls")
    contact = relationship("Contact", back_populates="calls")
    campaign = relationship("Campaign", back_populates="calls")
    recording = relationship("CallRecording", back_populates="call", uselist=False)

class CallRecording(Base):
    __tablename__ = "call_recordings"
    
    id = Column(Integer, primary_key=True, index=True)
    call_id = Column(Integer, ForeignKey("calls.id"), nullable=False)
    recording_sid = Column(String(100), unique=True)
    recording_url = Column(String(500))
    s3_url = Column(String(500))
    duration = Column(Integer)  # seconds
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    call = relationship("Call", back_populates="recording")