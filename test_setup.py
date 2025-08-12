#!/usr/bin/env python3
"""
Buttdialer Setup and Testing Script
Validates configuration and tests basic functionality
"""

import os
import sys
import requests
import asyncio
import asyncpg
from dotenv import load_dotenv

# Load environment variables
load_dotenv('buttdialer/backend/.env')

class ButtdialerTester:
    def __init__(self):
        self.backend_url = "http://localhost:8000"
        self.frontend_url = "http://localhost:3000"
        self.test_results = []
        
    def log_test(self, test_name, success, message=""):
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {message}")
        self.test_results.append({
            'test': test_name,
            'success': success,
            'message': message
        })
    
    def check_environment_variables(self):
        """Check if all required environment variables are set"""
        required_vars = [
            'SECRET_KEY',
            'DATABASE_URL',
            'TWILIO_ACCOUNT_SID',
            'TWILIO_AUTH_TOKEN',
            'TWILIO_PHONE_NUMBER',
            'TWILIO_API_KEY',
            'TWILIO_API_SECRET',
            'ELEVENLABS_API_KEY',
            'HUBSPOT_API_KEY'
        ]
        
        missing_vars = []
        for var in required_vars:
            if not os.getenv(var):
                missing_vars.append(var)
        
        success = len(missing_vars) == 0
        message = f"Missing variables: {', '.join(missing_vars)}" if missing_vars else "All variables present"
        self.log_test("Environment Variables", success, message)
        return success
    
    async def test_database_connection(self):
        """Test PostgreSQL database connection"""
        try:
            database_url = os.getenv('DATABASE_URL')
            conn = await asyncpg.connect(database_url)
            await conn.execute('SELECT 1')
            await conn.close()
            self.log_test("Database Connection", True, "Connected successfully")
            return True
        except Exception as e:
            self.log_test("Database Connection", False, str(e))
            return False
    
    def test_backend_health(self):
        """Test backend API health endpoint"""
        try:
            response = requests.get(f"{self.backend_url}/health", timeout=5)
            success = response.status_code == 200
            message = f"Status: {response.status_code}"
            self.log_test("Backend Health", success, message)
            return success
        except Exception as e:
            self.log_test("Backend Health", False, str(e))
            return False
    
    def test_frontend_availability(self):
        """Test frontend availability"""
        try:
            response = requests.get(self.frontend_url, timeout=5)
            success = response.status_code == 200
            message = f"Status: {response.status_code}"
            self.log_test("Frontend Availability", success, message)
            return success
        except Exception as e:
            self.log_test("Frontend Availability", False, str(e))
            return False
    
    def test_api_documentation(self):
        """Test API documentation availability"""
        try:
            response = requests.get(f"{self.backend_url}/docs", timeout=5)
            success = response.status_code == 200
            message = f"Swagger UI available at {self.backend_url}/docs"
            self.log_test("API Documentation", success, message)
            return success
        except Exception as e:
            self.log_test("API Documentation", False, str(e))
            return False
    
    def test_twilio_configuration(self):
        """Test Twilio API configuration"""
        try:
            from twilio.rest import Client
            account_sid = os.getenv('TWILIO_ACCOUNT_SID')
            auth_token = os.getenv('TWILIO_AUTH_TOKEN')
            
            client = Client(account_sid, auth_token)
            account = client.api.accounts(account_sid).fetch()
            
            success = account.status == 'active'
            message = f"Account status: {account.status}"
            self.log_test("Twilio Configuration", success, message)
            return success
        except Exception as e:
            self.log_test("Twilio Configuration", False, str(e))
            return False
    
    def test_elevenlabs_configuration(self):
        """Test ElevenLabs API configuration"""
        try:
            import httpx
            api_key = os.getenv('ELEVENLABS_API_KEY')
            headers = {'xi-api-key': api_key}
            
            response = requests.get(
                'https://api.elevenlabs.io/v1/user',
                headers=headers,
                timeout=10
            )
            
            success = response.status_code == 200
            message = f"API Status: {response.status_code}"
            self.log_test("ElevenLabs Configuration", success, message)
            return success
        except Exception as e:
            self.log_test("ElevenLabs Configuration", False, str(e))
            return False
    
    def test_hubspot_configuration(self):
        """Test HubSpot API configuration"""
        try:
            api_key = os.getenv('HUBSPOT_API_KEY')
            headers = {'Authorization': f'Bearer {api_key}'}
            
            response = requests.get(
                'https://api.hubapi.com/crm/v3/objects/contacts?limit=1',
                headers=headers,
                timeout=10
            )
            
            success = response.status_code == 200
            message = f"API Status: {response.status_code}"
            self.log_test("HubSpot Configuration", success, message)
            return success
        except Exception as e:
            self.log_test("HubSpot Configuration", False, str(e))
            return False
    
    def test_user_registration(self):
        """Test user registration endpoint"""
        try:
            test_user = {
                "email": "test@example.com",
                "password": "testpassword123",
                "first_name": "Test",
                "last_name": "User"
            }
            
            response = requests.post(
                f"{self.backend_url}/api/v1/auth/register",
                json=test_user,
                timeout=10
            )
            
            success = response.status_code in [200, 201, 400]  # 400 if user exists
            message = f"Status: {response.status_code}"
            self.log_test("User Registration", success, message)
            return success
        except Exception as e:
            self.log_test("User Registration", False, str(e))
            return False
    
    async def run_all_tests(self):
        """Run all tests and provide summary"""
        print("🚀 Starting Buttdialer Setup Tests...\n")
        
        # Environment tests
        self.check_environment_variables()
        
        # Database tests
        await self.test_database_connection()
        
        # Service availability tests
        self.test_backend_health()
        self.test_frontend_availability()
        self.test_api_documentation()
        
        # API configuration tests
        self.test_twilio_configuration()
        self.test_elevenlabs_configuration()
        self.test_hubspot_configuration()
        
        # Functionality tests
        self.test_user_registration()
        
        # Summary
        print("\n" + "="*50)
        print("TEST SUMMARY")
        print("="*50)
        
        passed = sum(1 for test in self.test_results if test['success'])
        total = len(self.test_results)
        
        print(f"Passed: {passed}/{total}")
        
        if passed == total:
            print("🎉 All tests passed! Your Buttdialer setup is ready.")
        else:
            print("⚠️  Some tests failed. Please check the configuration.")
            print("\nFailed tests:")
            for test in self.test_results:
                if not test['success']:
                    print(f"  - {test['test']}: {test['message']}")
        
        print("\nNext steps:")
        print("1. Start the backend: cd buttdialer/backend && uvicorn app.main:app --reload")
        print("2. Start the frontend: cd buttdialer/frontend && npm run dev")
        print("3. Visit http://localhost:3000 to access the application")
        
        return passed == total

if __name__ == "__main__":
    tester = ButtdialerTester()
    
    # Check if we're in the right directory
    if not os.path.exists('buttdialer'):
        print("❌ Error: Please run this script from the directory containing the 'buttdialer' folder")
        sys.exit(1)
    
    # Run tests
    try:
        asyncio.run(tester.run_all_tests())
    except KeyboardInterrupt:
        print("\n\n⚠️ Tests interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        sys.exit(1)