from pydantic import BaseModel, ConfigDict
from typing import Optional, List, Any, Dict
from datetime import datetime

# --- Review Comment Schemas ---

class ReviewCommentBase(BaseModel):
    comment: str

class ReviewCommentCreate(ReviewCommentBase):
    parent_comment_id: Optional[int] = None

class ReviewCommentResponse(ReviewCommentBase):
    id: int
    review_id: int
    review_frame_id: Optional[int]
    parent_comment_id: Optional[int]
    created_by: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    creator_name: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)

# --- Review Frame Schemas ---

class ReviewFrameBase(BaseModel):
    media_type: str
    timecode: Optional[float] = None
    annotation_data: Optional[Dict[str, Any]] = None
    description: Optional[str] = None
    image_data: Optional[str] = None

class ReviewFrameCreate(ReviewFrameBase):
    pass

class ReviewFrameUpdate(BaseModel):
    annotation_data: Optional[Dict[str, Any]] = None
    description: Optional[str] = None
    image_data: Optional[str] = None

class ReviewFrameResponse(ReviewFrameBase):
    id: int
    review_id: int
    created_by: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    creator_name: Optional[str] = None
    comments: List[ReviewCommentResponse] = []
    
    model_config = ConfigDict(from_attributes=True)

# --- Review Schemas ---

class ReviewBase(BaseModel):
    status: Optional[str] = 'pending'

class ReviewCreate(ReviewBase):
    version_id: int

class ReviewUpdate(ReviewBase):
    pass

class ReviewResponse(ReviewBase):
    id: int
    version_id: int
    created_by: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    creator_name: Optional[str] = None
    frames: List[ReviewFrameResponse] = []
    comments: List[ReviewCommentResponse] = []
    
    model_config = ConfigDict(from_attributes=True)
