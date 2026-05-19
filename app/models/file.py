from sqlalchemy import Column, String, Integer, ForeignKey, Text, BigInteger
from sqlalchemy.orm import relationship
from app.models.base import BaseModel

class File(BaseModel):
    __tablename__ = 'files'
    
    type = Column(String(16), nullable=False, default='file')
    code = Column(String(64), nullable=False)
    name = Column(String(256), nullable=False)
    file_extension = Column(String(64), nullable=True)
    
    file_path = Column(String(512), nullable=False)
    file_size = Column(Integer, nullable=True)
    file_hash = Column(String(64), nullable=True)
    mime_type = Column(String(128), nullable=True)
    
    project_id = Column(BigInteger, ForeignKey('projects.id'), nullable=False)
    version_id = Column(BigInteger, ForeignKey('versions.id'), nullable=False)
    task_id = Column(BigInteger, ForeignKey('tasks.id'), nullable=True)
    asset_id = Column(BigInteger, ForeignKey('assets.id'), nullable=True)
    shot_id = Column(BigInteger, ForeignKey('shots.id'), nullable=True)
    
    thumbnail_url = Column(String(256), nullable=True)
    description = Column(Text, nullable=True)
    
    # Relationships
    project = relationship('Project')
    version = relationship('Version')
    task = relationship('Task')
    asset = relationship('Asset')
    shot = relationship('Shot')