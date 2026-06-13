from sqlalchemy import Column, String, Integer, ForeignKey, Text, Boolean, DateTime, BigInteger
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from app.models.base import BaseModel

class Version(BaseModel):
    __tablename__ = 'versions'
    
    # type = Column(String(16), nullable=False, default='version')
    code = Column(String(64), nullable=False)
    name = Column(String(256), nullable=False)
    
    version_number = Column(String(64), nullable=False)
    # major_version = Column(Integer, nullable=False, default=0)
    # minor_version = Column(Integer, nullable=False, default=0)
    # patch_version = Column(Integer, nullable=False, default=0)
    
    # application = Column(String(64), nullable=True)
    # application_version = Column(String(64), nullable=True)
    
    project_id = Column(BigInteger, ForeignKey('projects.id'), nullable=False)
    publish_id = Column(BigInteger, ForeignKey('publish_types.id', ondelete='SET NULL'), nullable=True)
    
    asset_id = Column(BigInteger, ForeignKey('assets.id'), nullable=True)
    category_id = Column(BigInteger, ForeignKey('templates.id'), nullable=True)
    variant_id = Column(BigInteger, ForeignKey('variants.id'), nullable=True)
    
    episode_id = Column(BigInteger, ForeignKey('episodes.id'), nullable=True)
    editorial_id = Column(BigInteger, ForeignKey('editorials.id'), nullable=True)
    sequence_id = Column(BigInteger, ForeignKey('sequences.id'), nullable=True)
    shot_id = Column(BigInteger, ForeignKey('shots.id'), nullable=True)
    
    library_id = Column(BigInteger, ForeignKey('libraries.id'), nullable=True)
    cycle_id = Column(BigInteger, ForeignKey('cycles.id'), nullable=True)
    
    task_id = Column(BigInteger, ForeignKey('tasks.id', ondelete='CASCADE'), nullable=True)
    
    dependency_id = Column(BigInteger, ForeignKey('versions.id'), nullable=True)
    upstream_id = Column(BigInteger, ForeignKey('versions.id'), nullable=True)
    downstream_id = Column(BigInteger, ForeignKey('versions.id'), nullable=True)
    
    thumbnail_url = Column(String(256), nullable=True)
    movie_url = Column(String(256), nullable=True)
    image_path = Column(String(512), nullable=True)
    video_path = Column(String(512), nullable=True)
    
    # file_path = Column(String(512), nullable=True)
    # file_size = Column(Integer, nullable=True)
    # file_hash = Column(String(64), nullable=True)
    
    description = Column(Text, nullable=True)
    # changelog = Column(Text, nullable=True)
    tag = Column(String(64), nullable=True)
    # version_metadata = Column(JSONB, nullable=True, default={})
    
    # is_approved = Column(Boolean, nullable=False, default=False)
    # approved_by = Column(BigInteger, ForeignKey('users.id'), nullable=True)
    # approved_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships - REMOVED the 'files' relationship
    project = relationship('Project')
    publish_type = relationship('PublishType')
    asset = relationship('Asset')
    variant = relationship('Variant')
    episode = relationship('Episode')
    editorial = relationship('Editorial')
    sequence = relationship('Sequence')
    shot = relationship('Shot')
    library = relationship('Library')
    cycle = relationship('Cycle')
    task = relationship('Task')
    
    # approver = relationship('User', foreign_keys=[approved_by])
    
    dependency = relationship('Version', remote_side='Version.id', foreign_keys=[dependency_id])
    upstream = relationship('Version', remote_side='Version.id', foreign_keys=[upstream_id])
    downstream = relationship('Version', remote_side='Version.id', foreign_keys=[downstream_id])