from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_active_user, get_current_admin_user
from app.models.user import User
from app.models.team import Team, TeamMember
from app.schemas.team import TeamCreate, TeamResponse, TeamMemberAdd, TeamMemberResponse

router = APIRouter()

@router.post("/", response_model=TeamResponse)
async def create_team(
    team_data: TeamCreate,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Create a new team (admin only)"""
    team = Team(
        name=team_data.name,
        description=team_data.description
    )
    db.add(team)
    db.commit()
    db.refresh(team)
    
    # Add creator as team leader
    team_member = TeamMember(
        team_id=team.id,
        user_id=current_user.id,
        role="leader"
    )
    db.add(team_member)
    db.commit()
    
    return team

@router.get("/", response_model=List[TeamResponse])
async def get_teams(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get all teams (admin) or user's teams (agent)"""
    if current_user.role == "admin":
        teams = db.query(Team).all()
    else:
        # Get teams where user is a member
        team_ids = db.query(TeamMember.team_id).filter(
            TeamMember.user_id == current_user.id
        ).all()
        team_ids = [t[0] for t in team_ids]
        teams = db.query(Team).filter(Team.id.in_(team_ids)).all()
    
    return teams

@router.get("/{team_id}", response_model=TeamResponse)
async def get_team(
    team_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get team details"""
    team = db.query(Team).filter(Team.id == team_id).first()
    
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team not found"
        )
    
    # Check if user has access to this team
    if current_user.role != "admin":
        is_member = db.query(TeamMember).filter(
            TeamMember.team_id == team_id,
            TeamMember.user_id == current_user.id
        ).first()
        
        if not is_member:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to view this team"
            )
    
    return team

@router.post("/{team_id}/members", response_model=TeamMemberResponse)
async def add_team_member(
    team_id: int,
    member_data: TeamMemberAdd,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Add member to team"""
    team = db.query(Team).filter(Team.id == team_id).first()
    
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team not found"
        )
    
    # Check if user can add members (admin or team leader)
    if current_user.role != "admin":
        is_leader = db.query(TeamMember).filter(
            TeamMember.team_id == team_id,
            TeamMember.user_id == current_user.id,
            TeamMember.role == "leader"
        ).first()
        
        if not is_leader:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only team leaders can add members"
            )
    
    # Check if user exists
    user = db.query(User).filter(User.id == member_data.user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Check if already a member
    existing_member = db.query(TeamMember).filter(
        TeamMember.team_id == team_id,
        TeamMember.user_id == member_data.user_id
    ).first()
    
    if existing_member:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is already a team member"
        )
    
    # Add member
    team_member = TeamMember(
        team_id=team_id,
        user_id=member_data.user_id,
        role=member_data.role
    )
    db.add(team_member)
    db.commit()
    db.refresh(team_member)
    
    return team_member

@router.get("/{team_id}/members", response_model=List[TeamMemberResponse])
async def get_team_members(
    team_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get team members"""
    team = db.query(Team).filter(Team.id == team_id).first()
    
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team not found"
        )
    
    # Check access
    if current_user.role != "admin":
        is_member = db.query(TeamMember).filter(
            TeamMember.team_id == team_id,
            TeamMember.user_id == current_user.id
        ).first()
        
        if not is_member:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to view team members"
            )
    
    members = db.query(TeamMember).filter(TeamMember.team_id == team_id).all()
    return members

@router.delete("/{team_id}/members/{user_id}")
async def remove_team_member(
    team_id: int,
    user_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Remove member from team"""
    # Check if user can remove members (admin or team leader)
    if current_user.role != "admin":
        is_leader = db.query(TeamMember).filter(
            TeamMember.team_id == team_id,
            TeamMember.user_id == current_user.id,
            TeamMember.role == "leader"
        ).first()
        
        if not is_leader:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only team leaders can remove members"
            )
    
    # Find member
    member = db.query(TeamMember).filter(
        TeamMember.team_id == team_id,
        TeamMember.user_id == user_id
    ).first()
    
    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team member not found"
        )
    
    db.delete(member)
    db.commit()
    
    return {"message": "Member removed from team"}

@router.delete("/{team_id}")
async def delete_team(
    team_id: int,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Delete team (admin only)"""
    team = db.query(Team).filter(Team.id == team_id).first()
    
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team not found"
        )
    
    db.delete(team)
    db.commit()
    
    return {"message": "Team deleted"}