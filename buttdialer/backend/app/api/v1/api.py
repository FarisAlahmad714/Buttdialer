from fastapi import APIRouter

from app.api.v1.endpoints import auth, users, calls, teams, campaigns, contacts, compliance, crm

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(calls.router, prefix="/calls", tags=["calls"])
api_router.include_router(teams.router, prefix="/teams", tags=["teams"])
api_router.include_router(campaigns.router, prefix="/campaigns", tags=["campaigns"])
api_router.include_router(contacts.router, prefix="/contacts", tags=["contacts"])
api_router.include_router(compliance.router, prefix="/compliance", tags=["compliance"])
api_router.include_router(crm.router, prefix="/crm", tags=["crm"])