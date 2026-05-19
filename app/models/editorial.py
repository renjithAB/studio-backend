from sqlalchemy import Column, String, ForeignKey, Text, BigInteger
from sqlalchemy.orm import relationship
from app.models.base import BaseModel

class Editorial(BaseModel):
    __tablename__ = 'editorials'
    
    # type = Column(String(16), nullable=False, default='editorial')
    code = Column(String(64), nullable=False)
    name = Column(String(64), nullable=False)
    
    template_id = Column(BigInteger, ForeignKey('templates.id'), nullable=True)
    project_id = Column(BigInteger, ForeignKey('projects.id'), nullable=False)
    episode_id = Column(BigInteger, ForeignKey('episodes.id'), nullable=True)
    
    thumbnail_url = Column(String(256), nullable=True)
    description = Column(Text, nullable=True)
    tag = Column(String(64), nullable=True)
    
    # Relationships
    project = relationship('Project', back_populates='editorials')
    episode = relationship('Episode', back_populates='editorials')