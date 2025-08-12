# Buttdialer - Lean Business Dialer MVP

A modern, cost-effective dialer software designed for small businesses with integrated telephony, AI features, and team management capabilities.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                        BUTTDIALER MVP ARCHITECTURE                   │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌─────────────────┐         ┌─────────────────┐                   │
│  │   React Web     │         │   PostgreSQL    │                   │
│  │   Frontend      │         │   Database      │                   │
│  │  - Softphone    │         │  - Users/Teams  │                   │
│  │  - Dashboard    │         │  - Call Logs    │                   │
│  │  - Team Mgmt   │         │  - DNC Lists    │                   │
│  └────────┬────────┘         └────────┬────────┘                   │
│           │                            │                             │
│           └──────────┬─────────────────┘                            │
│                      │                                               │
│         ┌────────────▼──────────────┐                              │
│         │      FastAPI Backend      │                              │
│         │   (REST API Server)       │                              │
│         │  - Authentication/RBAC    │                              │
│         │  - Call Management        │                              │
│         │  - WebSocket Server       │                              │
│         └────────────┬──────────────┘                              │
│                      │                                               │
│    ┌─────────────────┴────────────────────────────┐                │
│    │                                               │                │
│    ▼                   ▼                   ▼       ▼                │
│ ┌──────────┐    ┌──────────┐    ┌──────────┐ ┌──────────┐        │
│ │  Twilio  │    │WebRTC/   │    │ElevenLabs│ │ HubSpot  │        │
│ │  Voice   │    │SimplePeer│    │   TTS    │ │   CRM    │        │
│ │   API    │    │          │    │   API    │ │   API    │        │
│ └──────────┘    └──────────┘    └──────────┘ └──────────┘        │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

## Features

### Core Telephony
- ✅ Outbound parallel dialing (2-3 numbers simultaneously)
- ✅ Browser-based WebRTC softphone
- ✅ Simple IVR with TwiML
- ✅ Call recording and logging
- ✅ Real-time call status updates

### AI Integration
- ✅ ElevenLabs TTS for pre-recorded messages
- ✅ Voice selection and customization
- ✅ Campaign message generation

### Team Management
- ✅ Role-based access control (admin/agent)
- ✅ Team creation and member management
- ✅ Real-time call monitoring for admins
- ✅ User management and permissions

### CRM Integration
- ✅ HubSpot Free Tier integration
- ✅ Contact sync and management
- ✅ Call logging to CRM
- ✅ Deal creation from calls

### Compliance
- ✅ Do Not Call (DNC) list management
- ✅ CSV upload for bulk DNC import
- ✅ TCPA calling hours validation
- ✅ Basic compliance reporting

## Tech Stack

- **Backend**: FastAPI (Python) with async support
- **Frontend**: React 18 with TypeScript and Tailwind CSS
- **Database**: PostgreSQL with SQLAlchemy ORM
- **WebRTC**: Twilio Voice SDK
- **Authentication**: JWT tokens
- **State Management**: Zustand
- **Styling**: Tailwind CSS with Headless UI

## Quick Start

### Prerequisites

1. **Node.js 18+** and **Python 3.9+**
2. **PostgreSQL 12+**
3. **API Keys**:
   - Twilio Account SID, Auth Token, Phone Number, API Key & Secret
   - ElevenLabs API Key
   - HubSpot API Key

### Backend Setup

1. **Install dependencies**:
   ```bash
   cd buttdialer/backend
   pip install -r requirements.txt
   ```

2. **Environment configuration**:
   ```bash
   cp .env.example .env
   # Edit .env with your API keys and database URL
   ```

3. **Database setup**:
   ```bash
   # Create database
   createdb buttdialer
   
   # Run migrations
   alembic upgrade head
   ```

4. **Start backend**:
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

### Frontend Setup

1. **Install dependencies**:
   ```bash
   cd buttdialer/frontend
   npm install
   ```

2. **Start development server**:
   ```bash
   npm run dev
   ```

The application will be available at:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

### First User Setup

1. Register first admin user through the UI
2. Configure team settings
3. Add team members
4. Upload DNC list (if needed)
5. Start making calls!

## API Configuration

### Twilio Setup

1. **Account Setup**:
   - Sign up for Twilio Free Trial ($15 credit)
   - Get Account SID and Auth Token from Console
   - Purchase/verify a phone number

2. **API Keys**:
   - Create API Key and Secret in Twilio Console
   - Configure webhook URLs:
     - Voice: `https://yourdomain.com/api/v1/calls/voice-webhook`
     - Status: `https://yourdomain.com/api/v1/calls/status-webhook`

3. **Environment Variables**:
   ```bash
   TWILIO_ACCOUNT_SID=your_account_sid
   TWILIO_AUTH_TOKEN=your_auth_token
   TWILIO_PHONE_NUMBER=+1234567890
   TWILIO_API_KEY=your_api_key
   TWILIO_API_SECRET=your_api_secret
   TWILIO_WEBHOOK_BASE_URL=https://yourdomain.com
   ```

### ElevenLabs Setup

1. **Account Setup**:
   - Sign up for free account (10,000 chars/month)
   - Get API key from profile

2. **Environment Variables**:
   ```bash
   ELEVENLABS_API_KEY=your_api_key
   ```

### HubSpot Setup

1. **Account Setup**:
   - Sign up for HubSpot Free CRM
   - Create private app or get API key

2. **Environment Variables**:
   ```bash
   HUBSPOT_API_KEY=your_api_key
   ```

## Testing Strategy

### Backend Testing

1. **Unit Tests**:
   ```bash
   cd buttdialer/backend
   pytest tests/ -v
   ```

2. **API Testing**:
   - Use the interactive docs at `/docs`
   - Test authentication endpoints first
   - Verify CRUD operations for all models

### Frontend Testing

1. **Component Testing**:
   ```bash
   cd buttdialer/frontend
   npm run test
   ```

2. **Manual Testing Checklist**:
   - [ ] User registration/login
   - [ ] Dashboard displays stats
   - [ ] Softphone connects and can make calls
   - [ ] Call history is recorded
   - [ ] Team management works
   - [ ] DNC list upload functions
   - [ ] CRM sync operates correctly

### Integration Testing

1. **Twilio Integration**:
   - Test outbound calls
   - Verify IVR responses
   - Check call recordings
   - Validate webhook callbacks

2. **WebRTC Testing**:
   - Browser compatibility check
   - Audio quality verification
   - Connection stability

## Deployment

### AWS Free Tier Deployment

1. **EC2 Setup** (t2.micro):
   ```bash
   # Install dependencies
   sudo apt update
   sudo apt install python3-pip nodejs npm postgresql-client
   
   # Clone and setup
   git clone your-repo
   cd buttdialer
   
   # Backend
   cd backend
   pip3 install -r requirements.txt
   
   # Frontend
   cd ../frontend
   npm install
   npm run build
   ```

2. **RDS PostgreSQL** (db.t2.micro):
   - Create RDS instance
   - Configure security groups
   - Update DATABASE_URL in .env

3. **Production Environment**:
   ```bash
   # Backend (using gunicorn)
   gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
   
   # Frontend (serve build files)
   npm install -g serve
   serve -s build -l 3000
   ```

4. **Reverse Proxy** (nginx):
   ```nginx
   server {
       listen 80;
       server_name yourdomain.com;
       
       location /api/ {
           proxy_pass http://localhost:8000;
       }
       
       location / {
           proxy_pass http://localhost:3000;
       }
   }
   ```

### Docker Deployment (Alternative)

```dockerfile
# Backend Dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

# Frontend Dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build
CMD ["npm", "run", "preview"]
```

## Cost Optimization

### Monthly Cost Estimate (MVP)
- **Twilio**: ~$10-15 (1000 minutes)
- **ElevenLabs**: Free (10K characters)
- **HubSpot**: Free tier
- **AWS EC2**: Free tier (12 months)
- **AWS RDS**: Free tier (12 months)
- **Total**: ~$10-15/month

### Scaling Recommendations

1. **Phase 2 Features**:
   - Batch calling campaigns
   - Advanced analytics
   - Mobile app
   - Multi-tenant support

2. **Infrastructure Scaling**:
   - Load balancer for multiple instances
   - Redis for session management
   - S3 for call recordings
   - CloudWatch for monitoring

3. **Cost Management**:
   - Monitor Twilio usage
   - Implement call volume limits
   - Use AWS cost alerts
   - Consider reserved instances

## Troubleshooting

### Common Issues

1. **WebRTC Not Working**:
   - Check HTTPS requirement
   - Verify Twilio credentials
   - Test browser permissions

2. **Database Connection**:
   - Verify PostgreSQL is running
   - Check connection string
   - Ensure database exists

3. **API Integration Issues**:
   - Verify API keys
   - Check network connectivity
   - Review error logs

### Logs and Monitoring

- Backend logs: Check uvicorn output
- Frontend errors: Browser developer console
- Database logs: PostgreSQL logs
- API calls: Network tab in browser

## Support and Documentation

- **API Documentation**: Available at `/docs` when backend is running
- **Twilio Docs**: https://www.twilio.com/docs/voice
- **ElevenLabs Docs**: https://docs.elevenlabs.io/
- **HubSpot API**: https://developers.hubspot.com/docs/api/overview

## License

MIT License - see LICENSE file for details.