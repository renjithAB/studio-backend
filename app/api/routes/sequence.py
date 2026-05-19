from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.sequence_service import SequenceService
from app.schemas.sequence import SequenceCreate, SequenceUpdate, SequenceResponse
from app.crud.crud_sequence import sequence as crud_sequence
from app.auth.dependencies import get_current_user, get_db
from app.models.users import User
from app.models.project import Project
from app.models.episode import Episode
from app.models.sequence import Sequence

router = APIRouter(prefix="/sequence", tags=["sequences"])
service = SequenceService()

@router.post("/", response_model=SequenceResponse, status_code=status.HTTP_201_CREATED)
def create_sequence(
    *,
    db: Session = Depends(get_db),
    sequence_in: SequenceCreate,
    current_user: User = Depends(get_current_user),
):
    """Create a new sequence with validation."""
    # 1. Check if project exists
    project = db.query(Project).filter(Project.id == sequence_in.project_id).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with id {sequence_in.project_id} not found"
        )

    # 2. Check if episode exists and belongs to the same project
    episode = db.query(Episode).filter(
        Episode.id == sequence_in.episode_id,
        Episode.project_id == sequence_in.project_id
    ).first()
    if not episode:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Episode with id {sequence_in.episode_id} not found in project {sequence_in.project_id}"
        )

    # 3. Check for duplicate code within the same project
    existing = db.query(Sequence).filter(
        Sequence.project_id == sequence_in.project_id,
        Sequence.code == sequence_in.code
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Sequence with code '{sequence_in.code}' already exists in project {sequence_in.project_id}"
        )

    # 4. Create sequence
    return service.create_sequence(
        db=db,
        sequence_in=sequence_in,
        created_by=current_user.id if current_user else None,
    )

@router.put("/{sequence_id}", response_model=SequenceResponse)
def update_sequence(
    sequence_id: int,
    data: SequenceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a sequence"""
    obj = crud_sequence.get(db, id=sequence_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Sequence not found")
    return crud_sequence.update(db, db_obj=obj, obj_in=data)