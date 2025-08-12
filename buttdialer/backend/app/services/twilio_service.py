from typing import List, Optional, Dict, Any
from twilio.rest import Client
from twilio.jwt.access_token import AccessToken
from twilio.jwt.access_token.grants import VoiceGrant
from twilio.twiml.voice_response import VoiceResponse, Dial, Gather
from datetime import datetime
import logging

from app.core.config import settings
from app.models.call import Call, CallRecording
from app.db.session import SessionLocal

logger = logging.getLogger(__name__)

class TwilioService:
    def __init__(self):
        self.client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        self.phone_number = settings.TWILIO_PHONE_NUMBER
        
    def generate_access_token(self, identity: str) -> str:
        """Generate access token for WebRTC client"""
        token = AccessToken(
            settings.TWILIO_ACCOUNT_SID,
            settings.TWILIO_API_KEY,
            settings.TWILIO_API_SECRET,
            identity=identity
        )
        
        voice_grant = VoiceGrant(
            outgoing_application_sid=settings.TWILIO_ACCOUNT_SID,
            incoming_allow=True
        )
        token.add_grant(voice_grant)
        
        return token.to_jwt()
    
    async def make_outbound_call(
        self, 
        to_number: str, 
        agent_id: int, 
        campaign_id: Optional[int] = None,
        contact_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """Initiate outbound call"""
        try:
            callback_url = f"{settings.TWILIO_WEBHOOK_BASE_URL}/api/v1/calls/voice-webhook"
            status_callback = f"{settings.TWILIO_WEBHOOK_BASE_URL}/api/v1/calls/status-webhook"
            
            # Create call record in database
            db = SessionLocal()
            call_record = Call(
                agent_id=agent_id,
                campaign_id=campaign_id,
                contact_id=contact_id,
                direction='outbound',
                from_number=self.phone_number,
                to_number=to_number,
                status='initiated'
            )
            db.add(call_record)
            db.commit()
            db.refresh(call_record)
            
            # Initiate Twilio call
            twilio_call = self.client.calls.create(
                to=to_number,
                from_=self.phone_number,
                url=callback_url,
                status_callback=status_callback,
                status_callback_event=['initiated', 'ringing', 'answered', 'completed'],
                status_callback_method='POST',
                method='POST',
                timeout=30,
                record=True,
                recording_status_callback=f"{settings.TWILIO_WEBHOOK_BASE_URL}/api/v1/calls/recording-webhook",
                recording_status_callback_method='POST'
            )
            
            # Update call record with Twilio SID
            call_record.twilio_call_sid = twilio_call.sid
            db.commit()
            
            result = {
                'success': True,
                'call_sid': twilio_call.sid,
                'call_id': call_record.id,
                'status': twilio_call.status
            }
            
            db.close()
            return result
            
        except Exception as e:
            logger.error(f"Error making outbound call: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def make_parallel_calls(
        self, 
        phone_numbers: List[str], 
        agent_id: int, 
        campaign_id: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Make multiple parallel calls (2-3 max for MVP)"""
        results = []
        # Limit to 3 parallel calls
        for number in phone_numbers[:3]:
            result = await self.make_outbound_call(number, agent_id, campaign_id)
            results.append(result)
        return results
    
    def generate_ivr_response(self, digits: Optional[str] = None) -> str:
        """Generate IVR TwiML response"""
        response = VoiceResponse()
        
        if not digits:
            # Initial IVR prompt
            gather = Gather(
                num_digits=1,
                action='/api/v1/calls/ivr-handler',
                method='POST',
                timeout=5
            )
            gather.say(
                "Thank you for calling. Press 1 to speak with an agent. Press 2 to leave a message.",
                voice='alice'
            )
            response.append(gather)
            # If no input, repeat
            response.redirect('/api/v1/calls/voice-webhook')
        else:
            if digits == '1':
                # Connect to agent
                response.say("Connecting you to an agent. Please wait.", voice='alice')
                dial = Dial(
                    action='/api/v1/calls/dial-complete',
                    timeout=30,
                    record='record-from-answer'
                )
                # Connect to available agent via WebRTC client
                dial.client('agent-client')
                response.append(dial)
            elif digits == '2':
                # Voicemail
                response.say(
                    "Please leave your message after the beep. Press any key when finished.",
                    voice='alice'
                )
                response.record(
                    action='/api/v1/calls/voicemail-complete',
                    method='POST',
                    max_length=120,
                    finish_on_key='*'
                )
            else:
                # Invalid input
                response.say("Invalid selection. Please try again.", voice='alice')
                response.redirect('/api/v1/calls/voice-webhook')
        
        return str(response)
    
    async def update_call_status(self, call_sid: str, status: str) -> None:
        """Update call status in database"""
        db = SessionLocal()
        call = db.query(Call).filter(Call.twilio_call_sid == call_sid).first()
        
        if call:
            call.status = status
            
            if status == 'answered':
                call.answered_at = datetime.utcnow()
            elif status in ['completed', 'failed', 'busy', 'no-answer']:
                call.ended_at = datetime.utcnow()
                if call.answered_at and call.ended_at:
                    duration = (call.ended_at - call.answered_at).total_seconds()
                    call.duration = int(duration)
            
            db.commit()
        
        db.close()
    
    async def save_recording(self, call_sid: str, recording_sid: str, recording_url: str) -> None:
        """Save call recording information"""
        db = SessionLocal()
        call = db.query(Call).filter(Call.twilio_call_sid == call_sid).first()
        
        if call:
            recording = CallRecording(
                call_id=call.id,
                recording_sid=recording_sid,
                recording_url=recording_url
            )
            db.add(recording)
            db.commit()
        
        db.close()
    
    def end_call(self, call_sid: str) -> bool:
        """End an active call"""
        try:
            self.client.calls(call_sid).update(status='completed')
            return True
        except Exception as e:
            logger.error(f"Error ending call: {str(e)}")
            return False

# Singleton instance
twilio_service = TwilioService()