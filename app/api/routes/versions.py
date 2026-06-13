from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
import os
import io
from app.core.config import UPLOAD_DIR
from app.schemas.version import VersionCreate, VersionUpdate, VersionResponse
from app.crud.crud_version import version as crud_version
from app.auth.dependencies import get_current_user, get_db
from app.models.users import User

router = APIRouter()

@router.post("/", response_model=VersionResponse, status_code=status.HTTP_201_CREATED)
def create_version(
    *,
    db: Session = Depends(get_db),
    version_in: VersionCreate,
    current_user: User = Depends(get_current_user)
):
    """
    Create a new version under a publish type.
    """
    # Verify the code is format-validated or handle custom logic if needed
    return crud_version.create(
        db=db,
        obj_in=version_in,
        created_by=current_user.id if current_user else None
    )

@router.get("/{version_id}", response_model=VersionResponse)
def get_version(
    version_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a version by ID"""
    obj = crud_version.get(db, id=version_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Version not found")
    return obj

@router.put("/{version_id}", response_model=VersionResponse)
def update_version(
    version_id: int,
    data: VersionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a version"""
    obj = crud_version.get(db, id=version_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Version not found")
    return crud_version.update(
        db, 
        db_obj=obj, 
        obj_in=data, 
        updated_by=current_user.id if current_user else None
    )

def build_version_hierarchy_path(version) -> str:
    parts = ["projects", version.project.code if version.project else "unknown"]
    
    if version.asset_id and version.asset:
        parts.extend(["assets"])
        if hasattr(version.asset, 'category') and version.asset.category:
            parts.append(version.asset.category.code)
        parts.append(version.asset.code)
    elif version.shot_id and version.shot:
        parts.extend(["shots"])
        if hasattr(version.shot, 'sequence') and version.shot.sequence:
            if hasattr(version.shot.sequence, 'episode') and version.shot.sequence.episode:
                parts.extend(["episodes", version.shot.sequence.episode.code])
            parts.extend(["sequences", version.shot.sequence.code])
        parts.append(version.shot.code)
    
    if version.task_id and version.task:
        parts.extend(["tasks", version.task.code])
        
    if version.variant_id and version.variant:
        parts.extend(["variants", version.variant.code])
        
    if version.publish_id and version.publish_type:
        parts.extend(["publishes", version.publish_type.code])
        
    parts.append(version.version_number)
    return "/".join(parts)

@router.post("/{version_id}/upload", response_model=VersionResponse)
async def upload_version_files(
    version_id: int,
    image: UploadFile = File(None),
    video: UploadFile = File(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Upload high-res image and video for a version, and generate a thumbnail."""
    obj = crud_version.get(db, id=version_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Version not found")
        
    hierarchy_path = build_version_hierarchy_path(obj)
    full_dir_path = UPLOAD_DIR / hierarchy_path
    
    os.makedirs(full_dir_path, exist_ok=True)
    
    updated_data = {}
    
    if image:
        ext = os.path.splitext(image.filename)[1].lower()
        if ext not in ['.png', '.jpg', '.jpeg', '.bmp']:
            raise HTTPException(status_code=400, detail=f"Unsupported image type: {ext}")
            
        img_filename = f"image{ext}"
        img_path = full_dir_path / img_filename
        
        data = await image.read()
        with open(img_path, "wb") as f:
            f.write(data)
            
        updated_data['image_path'] = f"/uploads/{hierarchy_path}/{img_filename}"
        
        from PIL import Image
        try:
            img = Image.open(io.BytesIO(data))
            if img.mode in ("RGBA", "P"):
                img = img.convert("RGBA")
            else:
                img = img.convert("RGB")
            
            img.thumbnail((256, 256), Image.Resampling.LANCZOS)
            thumb_filename = "thumb.webp"
            thumb_path = full_dir_path / thumb_filename
            
            output = io.BytesIO()
            img.save(output, format="WEBP", quality=80, method=4)
            with open(thumb_path, "wb") as f:
                f.write(output.getvalue())
                
            updated_data['thumbnail_url'] = f"/uploads/{hierarchy_path}/{thumb_filename}"
        except Exception as e:
            print(f"Error generating thumbnail: {e}")
            
    if video:
        ext = os.path.splitext(video.filename)[1].lower()
        if ext not in ['.mp4', '.mov', '.avi']:
            raise HTTPException(status_code=400, detail=f"Unsupported video type: {ext}")
            
        vid_filename = f"video{ext}"
        vid_path = full_dir_path / vid_filename
        
        with open(vid_path, "wb") as f:
            f.write(await video.read())
            
        updated_data['video_path'] = f"/uploads/{hierarchy_path}/{vid_filename}"
        updated_data['movie_url'] = updated_data['video_path']
        
    if not updated_data:
        raise HTTPException(status_code=400, detail="No files provided")
        
    return crud_version.update(
        db, 
        db_obj=obj, 
        obj_in=VersionUpdate(**updated_data), 
        updated_by=current_user.id if current_user else None
    )
