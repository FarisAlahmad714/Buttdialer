import httpx
import logging
from typing import Optional, Dict, Any
import base64
from app.core.config import settings

logger = logging.getLogger(__name__)

class ElevenLabsService:
    def __init__(self):
        self.api_key = settings.ELEVENLABS_API_KEY
        self.base_url = "https://api.elevenlabs.io/v1"
        self.headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": self.api_key
        }
        
    async def text_to_speech(
        self, 
        text: str, 
        voice_id: str = "21m00Tcm4TlvDq8ikWAM",  # Rachel voice (default)
        model_id: str = "eleven_monolingual_v1"
    ) -> Optional[bytes]:
        """Convert text to speech using ElevenLabs API"""
        try:
            url = f"{self.base_url}/text-to-speech/{voice_id}"
            
            payload = {
                "text": text,
                "model_id": model_id,
                "voice_settings": {
                    "stability": 0.5,
                    "similarity_boost": 0.75
                }
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url,
                    json=payload,
                    headers=self.headers,
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    return response.content
                else:
                    logger.error(f"ElevenLabs API error: {response.status_code} - {response.text}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error in text_to_speech: {str(e)}")
            return None
    
    async def get_voices(self) -> Optional[Dict[str, Any]]:
        """Get available voices from ElevenLabs"""
        try:
            url = f"{self.base_url}/voices"
            headers = {
                "Accept": "application/json",
                "xi-api-key": self.api_key
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.get(url, headers=headers)
                
                if response.status_code == 200:
                    return response.json()
                else:
                    logger.error(f"Error getting voices: {response.status_code}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error getting voices: {str(e)}")
            return None
    
    async def get_user_info(self) -> Optional[Dict[str, Any]]:
        """Get user subscription info including character usage"""
        try:
            url = f"{self.base_url}/user"
            headers = {
                "Accept": "application/json",
                "xi-api-key": self.api_key
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.get(url, headers=headers)
                
                if response.status_code == 200:
                    return response.json()
                else:
                    logger.error(f"Error getting user info: {response.status_code}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error getting user info: {str(e)}")
            return None
    
    async def generate_campaign_message(
        self,
        template: str,
        contact_name: str,
        voice_id: str = "21m00Tcm4TlvDq8ikWAM"
    ) -> Optional[bytes]:
        """Generate personalized campaign message"""
        # Replace placeholders in template
        message = template.replace("{name}", contact_name)
        
        # Ensure we don't exceed free tier limits (10,000 chars/month)
        if len(message) > 500:
            logger.warning("Message too long, truncating to 500 characters")
            message = message[:500]
        
        return await self.text_to_speech(message, voice_id)
    
    def audio_to_base64(self, audio_bytes: bytes) -> str:
        """Convert audio bytes to base64 string for storage/transmission"""
        return base64.b64encode(audio_bytes).decode('utf-8')
    
    def base64_to_audio(self, base64_string: str) -> bytes:
        """Convert base64 string back to audio bytes"""
        return base64.b64decode(base64_string)

# Singleton instance
elevenlabs_service = ElevenLabsService()