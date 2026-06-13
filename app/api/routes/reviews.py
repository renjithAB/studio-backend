from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.auth.dependencies import get_current_user
from app.models.users import User
from app.schemas.review import (
    ReviewCreate, ReviewUpdate, ReviewResponse, 
    ReviewFrameCreate, ReviewFrameUpdate, ReviewFrameResponse,
    ReviewCommentCreate, ReviewCommentResponse
)
from app.crud.review import review as crud_review
from app.models.version import Version
from app.services.hierarchy_service import HierarchyService

router = APIRouter()

from app.models.project import Project
from app.models.task import Task
from app.models.variant import Variant
from app.models.publish_types import PublishType

@router.get("/versions", response_model=dict)
def list_all_versions(
    skip: int = Query(0, ge=0), 
    limit: int = Query(20, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all versions with their hierarchy metadata."""
    query = db.query(Version).filter(Version.is_active == True)
    total = query.count()
    versions = query.order_by(Version.id.desc()).offset(skip).limit(limit).all()
    
    results = []
    for ver in versions:
        meta = HierarchyService._get_model_data(ver)
        meta["id"] = ver.id
        meta["code"] = ver.code
        meta["name"] = ver.name
        
        # Fetch related codes
        if meta.get("project_id"):
            proj = db.query(Project).filter(Project.id == meta["project_id"]).first()
            if proj: meta["project_code"] = proj.code
        if meta.get("task_id"):
            task = db.query(Task).filter(Task.id == meta["task_id"]).first()
            if task: meta["task_code"] = task.code
        if meta.get("variant_id"):
            var = db.query(Variant).filter(Variant.id == meta["variant_id"]).first()
            if var: meta["variant_code"] = var.code
        if meta.get("publish_id"):
            pub = db.query(PublishType).filter(PublishType.id == meta["publish_id"]).first()
            if pub: meta["publish_code"] = pub.code
            
        results.append(meta)
        
    return {
        "items": results,
        "total": total,
        "skip": skip,
        "limit": limit
    }

@router.get("/version/{version_id}", response_model=List[ReviewResponse])
def get_reviews_by_version(
    version_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return crud_review.get_by_version(db, version_id)

@router.post("/", response_model=ReviewResponse)
def create_review(
    obj_in: ReviewCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        return crud_review.create(db, obj_in, current_user.id)
    except Exception as e:
        import traceback
        with open("error.log", "w") as f:
            traceback.print_exc(file=f)
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{review_id}", response_model=ReviewResponse)
def update_review(
    review_id: int,
    obj_in: ReviewUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        return crud_review.update(db, review_id, obj_in)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{review_id}/frames", response_model=ReviewFrameResponse)
def add_review_frame(
    review_id: int,
    obj_in: ReviewFrameCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return crud_review.add_frame(db, review_id, obj_in, current_user.id)

@router.put("/frames/{frame_id}", response_model=ReviewFrameResponse)
def update_review_frame(
    frame_id: int,
    obj_in: ReviewFrameUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return crud_review.update_frame(db, frame_id, obj_in)

@router.delete("/frames/{frame_id}")
def delete_review_frame(
    frame_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    crud_review.delete_frame(db, frame_id)
    return {"status": "ok"}

@router.post("/{review_id}/comments", response_model=ReviewCommentResponse)
def add_review_comment(
    review_id: int,
    obj_in: ReviewCommentCreate,
    frame_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return crud_review.add_comment(db, review_id, frame_id, obj_in, current_user.id)
