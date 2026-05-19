from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.shot_service import ShotService
from app.schemas.shot import ShotCreate, ShotUpdate, ShotResponse
from app.crud.crud_shot import shot as crud_shot
from app.auth.dependencies import get_current_user, get_db
from app.models.users import User
from app.models.project import Project
from app.models.sequence import Sequence
from app.models.shot import Shot

router = APIRouter(prefix="/shot", tags=["shots"])
service = ShotService()

@router.post("/", response_model=ShotResponse, status_code=status.HTTP_201_CREATED)
def create_shot(
    *,
    db: Session = Depends(get_db),
    shot_in: ShotCreate,
    current_user: User = Depends(get_current_user),
):
    """Create a new shot with validation."""
    # 1. Check if project exists
    project = db.query(Project).filter(Project.id == shot_in.project_id).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with id {shot_in.project_id} not found"
        )

    # 2. Check if sequence exists and belongs to the same project
    sequence = db.query(Sequence).filter(
        Sequence.id == shot_in.sequence_id,
        Sequence.project_id == shot_in.project_id
    ).first()
    if not sequence:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Sequence with id {shot_in.sequence_id} not found in project {shot_in.project_id}"
        )

    # 3. Check for duplicate code within the same project
    existing = db.query(Shot).filter(
        Shot.project_id == shot_in.project_id,
        Shot.code == shot_in.code
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Shot with code '{shot_in.code}' already exists in project {shot_in.project_id}"
        )

    # 4. Create shot
    return service.create_shot(
        db=db,
        shot_in=shot_in,
        created_by=current_user.id if current_user else None,
    )

@router.put("/{shot_id}", response_model=ShotResponse)
def update_shot(
    shot_id: int,
    data: ShotUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a shot"""
    obj = crud_shot.get(db, id=shot_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Shot not found")
    return crud_shot.update(db, db_obj=obj, obj_in=data)