from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app.services.episode_service import EpisodeService
from app.schemas.episode import EpisodeCreate, EpisodeUpdate, EpisodeResponse
from app.auth.dependencies import get_current_user, get_db
from app.models.users import User 
from app.models.project import Project
from app.models.episode import Episode
from app.crud.crud_episode import episode as crud_episode

router = APIRouter()
service = EpisodeService()

@router.post("/", response_model=EpisodeResponse, status_code=status.HTTP_201_CREATED)
def create_episode(
    *,
    db: Session = Depends(get_db),
    episode_in: EpisodeCreate,
    current_user: User = Depends(get_current_user),  # optional auth
):
    """Create a new episode."""
    # Optional: check if project exists
    project = db.query(Project).filter(Project.id == episode_in.project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    existing = db.query(Episode).filter(
        Episode.project_id == episode_in.project_id,
        Episode.code == episode_in.code
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Episode with code '{episode_in.code}' already exists in project {episode_in.project_id}"
        )

    return service.create_episode(
        db=db,
        episode_in=episode_in,
        created_by=current_user.id if current_user else None,
    )

@router.put("/{episode_id}", response_model=EpisodeResponse)
def update_episode(
    episode_id: int,
    data: EpisodeUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update an episode"""
    obj = crud_episode.get(db, id=episode_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Episode not found")
    return crud_episode.update(db, db_obj=obj, obj_in=data)
