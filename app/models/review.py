from sqlalchemy import Column, String, Integer, ForeignKey, Text, Boolean, DateTime, BigInteger, Float
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from app.models.base import BaseModel

class Review(BaseModel):
    __tablename__ = 'reviews'
    
    version_id = Column(BigInteger, ForeignKey('versions.id', ondelete='CASCADE'), nullable=False)
    created_by = Column(BigInteger, ForeignKey('users.id'), nullable=False)
    status = Column(String(64), nullable=False, default='pending')
    
    # Relationships
    version = relationship('Version', backref='reviews')
    creator = relationship('User', foreign_keys=[created_by])
    frames = relationship('ReviewFrame', back_populates='review', cascade='all, delete-orphan')
    comments = relationship('ReviewComment', back_populates='review', cascade='all, delete-orphan')

class ReviewFrame(BaseModel):
    __tablename__ = 'review_frames'
    
    review_id = Column(BigInteger, ForeignKey('reviews.id', ondelete='CASCADE'), nullable=False)
    media_type = Column(String(16), nullable=False) # 'image' or 'video'
    timecode = Column(Float, nullable=True) # timestamp in seconds for videos
    annotation_data = Column(JSONB, nullable=True) # stores drawing JSON
    description = Column(Text, nullable=True) # user's description in the cart
    image_data = Column(Text, nullable=True) # base64 data url of the drawn frame for quick preview
    created_by = Column(BigInteger, ForeignKey('users.id'), nullable=False)
    
    # Relationships
    review = relationship('Review', back_populates='frames')
    creator = relationship('User', foreign_keys=[created_by])
    comments = relationship('ReviewComment', back_populates='frame', cascade='all, delete-orphan')

class ReviewComment(BaseModel):
    __tablename__ = 'review_comments'
    
    review_id = Column(BigInteger, ForeignKey('reviews.id', ondelete='CASCADE'), nullable=False)
    review_frame_id = Column(BigInteger, ForeignKey('review_frames.id', ondelete='CASCADE'), nullable=True)
    parent_comment_id = Column(BigInteger, ForeignKey('review_comments.id', ondelete='CASCADE'), nullable=True)
    comment = Column(Text, nullable=False)
    created_by = Column(BigInteger, ForeignKey('users.id'), nullable=False)
    
    # Relationships
    review = relationship('Review', back_populates='comments')
    frame = relationship('ReviewFrame', back_populates='comments')
    creator = relationship('User', foreign_keys=[created_by])
    replies = relationship('ReviewComment', backref='parent', remote_side='ReviewComment.id')
