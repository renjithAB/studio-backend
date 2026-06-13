from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.auth.dependencies import get_current_user
from app.models.media_token import MediaToken
from app.core.config import UPLOAD_DIR
from fastapi.responses import FileResponse
from pydantic import BaseModel
import uuid
from datetime import datetime, timedelta, timezone
import os

router = APIRouter()

class TokenRequest(BaseModel):
    file_path: str

@router.post("/token")
def generate_media_token(
    request: TokenRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    # Validate that the file actually exists
    # The file_path from DB usually starts with /uploads/
    clean_path = request.file_path
    if clean_path.startswith("/uploads/"):
        clean_path = clean_path.replace("/uploads/", "", 1)
        
    full_path = UPLOAD_DIR / clean_path
    if not full_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
        
    # Generate token
    token = MediaToken(
        token=uuid.uuid4(),
        file_path=clean_path,
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=10) # 10 minute expiry
    )
    db.add(token)
    db.commit()
    
    return {"url": f"/api/v1/media/view/{token.token}"}

@router.get("/view/{token_id}")
def view_media(token_id: uuid.UUID, db: Session = Depends(get_db)):
    token = db.query(MediaToken).filter(MediaToken.token == token_id).first()
    
    if not token:
        raise HTTPException(status_code=404, detail="Invalid token")
        
    if token.is_used:
        raise HTTPException(status_code=403, detail="This link has already been used.")
        
    if token.expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=403, detail="This link has expired.")
        
    # Mark as used immediately to enforce single-use
    token.is_used = True
    db.commit()
    
    full_path = UPLOAD_DIR / token.file_path
    if not full_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
        
    # Determine media type based on extension for proper serving
    ext = os.path.splitext(token.file_path)[1].lower()
    media_type = "application/octet-stream"
    if ext in ['.png', '.jpg', '.jpeg', '.bmp']:
        media_type = f"image/{ext[1:].replace('jpg', 'jpeg')}"
    elif ext in ['.mp4', '.mov', '.avi']:
        media_type = f"video/{ext[1:]}"
        
    # For video, we should ideally support range requests, but FileResponse handles basic range requests natively in newer FastAPI/Starlette versions.
    return FileResponse(str(full_path), media_type=media_type)
