# app/api/routes/images.py
from fastapi import APIRouter, HTTPException, UploadFile, File
from fastapi.responses import FileResponse
from pathlib import Path
import os
import uuid
import shutil
from app.core.config import PROJECT_THUMBNAIL_DIR, HIERARCHY_THUMBNAIL_DIR
from app.core.image_utils import resize_image
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/projects/thumbnails/{filename}")
async def get_project_thumbnail(filename: str):
    """Serve project thumbnail images with proper CORS headers"""
    # Security: Prevent directory traversal
    if ".." in filename or "/" in filename:
        raise HTTPException(status_code=400, detail="Invalid filename")
    
    file_path = PROJECT_THUMBNAIL_DIR / filename
    
    if not file_path.exists():
        logger.error(f"Thumbnail not found: {file_path}")
        raise HTTPException(status_code=404, detail="Thumbnail not found")
    
    return FileResponse(
        path=file_path,
        headers={
            "Access-Control-Allow-Origin": "*",
            "Cache-Control": "public, max-age=31536000",
        }
    )

@router.get("/hierarchy/thumbnails/{filename}")
async def get_hierarchy_thumbnail(filename: str):
    """Serve hierarchy thumbnail images"""
    if ".." in filename or "/" in filename:
        raise HTTPException(status_code=400, detail="Invalid filename")
    
    file_path = HIERARCHY_THUMBNAIL_DIR / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Thumbnail not found")
    
    return FileResponse(
        path=file_path,
        headers={
            "Access-Control-Allow-Origin": "*",
            "Cache-Control": "public, max-age=31536000",
        }
    )

@router.post("/thumbnails/upload", status_code=201)
async def upload_thumbnail(file: UploadFile = File(...)):
    """Upload and resize a thumbnail for any hierarchy entity"""
    # 1. Validate file type
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    # 2. Generate unique filename (enforce .webp for smallest size)
    filename = f"{uuid.uuid4()}.webp"
    final_path = HIERARCHY_THUMBNAIL_DIR / filename
    
    try:
        # Read the file directly into memory
        data = await file.read()
        
        # 3. Resize and compress image using PIL
        from PIL import Image
        import io
        
        try:
            img = Image.open(io.BytesIO(data))
            
            if img.mode in ("RGBA", "P"):
                img = img.convert("RGBA")
            else:
                img = img.convert("RGB")
                
            # Resize image to max 256x256
            img.thumbnail((256, 256), Image.Resampling.LANCZOS)
            
            # Save as WEBP for best compression (< 50kb easily)
            output = io.BytesIO()
            img.save(output, format="WEBP", quality=80, method=4)
            resized_data = output.getvalue()
        except Exception as e:
            logger.error(f"Error resizing image: {e}")
            resized_data = data # fallback to original if resize fails
            
        # 4. Save final file
        with open(final_path, "wb") as f:
            f.write(resized_data)
            
        # Return relative URL (compatible with frontend expectation)
        return {"url": f"/api/v1/images/hierarchy/thumbnails/{filename}"}
            
    except Exception as e:
        logger.error(f"Thumbnail upload error: {e}")
        raise HTTPException(status_code=500, detail="Failed to process image")