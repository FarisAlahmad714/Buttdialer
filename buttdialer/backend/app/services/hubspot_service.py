import httpx
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime
from app.core.config import settings

logger = logging.getLogger(__name__)

class HubSpotService:
    def __init__(self):
        self.api_key = settings.HUBSPOT_API_KEY
        self.base_url = "https://api.hubapi.com"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    async def create_or_update_contact(
        self,
        email: Optional[str] = None,
        phone: Optional[str] = None,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        company: Optional[str] = None,
        custom_properties: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """Create or update a contact in HubSpot"""
        try:
            properties = {}
            
            if email:
                properties["email"] = email
            if phone:
                properties["phone"] = phone
            if first_name:
                properties["firstname"] = first_name
            if last_name:
                properties["lastname"] = last_name
            if company:
                properties["company"] = company
                
            if custom_properties:
                properties.update(custom_properties)
            
            # First, try to find existing contact by email or phone
            existing_contact = None
            if email:
                existing_contact = await self.get_contact_by_email(email)
            elif phone:
                existing_contact = await self.search_contacts(f"phone:{phone}")
                if existing_contact and existing_contact.get('results'):
                    existing_contact = existing_contact['results'][0]
            
            url = f"{self.base_url}/crm/v3/objects/contacts"
            
            if existing_contact:
                # Update existing contact
                contact_id = existing_contact.get('id')
                url = f"{url}/{contact_id}"
                
                async with httpx.AsyncClient() as client:
                    response = await client.patch(
                        url,
                        json={"properties": properties},
                        headers=self.headers
                    )
            else:
                # Create new contact
                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        url,
                        json={"properties": properties},
                        headers=self.headers
                    )
            
            if response.status_code in [200, 201]:
                return response.json()
            else:
                logger.error(f"HubSpot API error: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Error creating/updating contact: {str(e)}")
            return None
    
    async def get_contact_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get contact by email"""
        try:
            url = f"{self.base_url}/crm/v3/objects/contacts/{email}?idProperty=email"
            
            async with httpx.AsyncClient() as client:
                response = await client.get(url, headers=self.headers)
                
                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 404:
                    return None
                else:
                    logger.error(f"Error getting contact: {response.status_code}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error getting contact by email: {str(e)}")
            return None
    
    async def search_contacts(self, query: str) -> Optional[Dict[str, Any]]:
        """Search contacts"""
        try:
            url = f"{self.base_url}/crm/v3/objects/contacts/search"
            
            payload = {
                "query": query,
                "limit": 10,
                "properties": ["email", "firstname", "lastname", "phone", "company"]
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url,
                    json=payload,
                    headers=self.headers
                )
                
                if response.status_code == 200:
                    return response.json()
                else:
                    logger.error(f"Error searching contacts: {response.status_code}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error searching contacts: {str(e)}")
            return None
    
    async def log_call_activity(
        self,
        contact_id: str,
        call_duration: int,
        call_notes: str,
        call_disposition: str,
        call_time: datetime
    ) -> Optional[Dict[str, Any]]:
        """Log a call as an activity in HubSpot"""
        try:
            url = f"{self.base_url}/crm/v3/objects/calls"
            
            # Convert duration to milliseconds
            duration_ms = call_duration * 1000
            
            properties = {
                "hs_timestamp": int(call_time.timestamp() * 1000),
                "hs_call_title": f"Call - {call_disposition}",
                "hs_call_body": call_notes,
                "hs_call_duration": str(duration_ms),
                "hs_call_from_number": settings.TWILIO_PHONE_NUMBER,
                "hs_call_to_number": "",  # Will be set from contact
                "hs_call_status": "COMPLETED",
                "hs_call_disposition": call_disposition
            }
            
            associations = {
                "to": [
                    {
                        "id": contact_id,
                        "type": "contact"
                    }
                ]
            }
            
            payload = {
                "properties": properties,
                "associations": associations
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url,
                    json=payload,
                    headers=self.headers
                )
                
                if response.status_code in [200, 201]:
                    return response.json()
                else:
                    logger.error(f"Error logging call: {response.status_code} - {response.text}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error logging call activity: {str(e)}")
            return None
    
    async def sync_contacts_to_database(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Sync contacts from HubSpot to local database"""
        try:
            url = f"{self.base_url}/crm/v3/objects/contacts"
            params = {
                "limit": limit,
                "properties": "email,firstname,lastname,phone,company"
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    url,
                    params=params,
                    headers=self.headers
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return data.get('results', [])
                else:
                    logger.error(f"Error syncing contacts: {response.status_code}")
                    return []
                    
        except Exception as e:
            logger.error(f"Error syncing contacts: {str(e)}")
            return []
    
    async def create_deal(
        self,
        deal_name: str,
        amount: float,
        contact_id: str,
        pipeline_stage: str = "appointmentscheduled"
    ) -> Optional[Dict[str, Any]]:
        """Create a deal in HubSpot"""
        try:
            url = f"{self.base_url}/crm/v3/objects/deals"
            
            properties = {
                "dealname": deal_name,
                "amount": str(amount),
                "dealstage": pipeline_stage,
                "pipeline": "default"
            }
            
            associations = {
                "to": [
                    {
                        "id": contact_id,
                        "type": "contact"
                    }
                ]
            }
            
            payload = {
                "properties": properties,
                "associations": associations
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url,
                    json=payload,
                    headers=self.headers
                )
                
                if response.status_code in [200, 201]:
                    return response.json()
                else:
                    logger.error(f"Error creating deal: {response.status_code}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error creating deal: {str(e)}")
            return None

# Singleton instance
hubspot_service = HubSpotService()