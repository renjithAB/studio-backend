from sqlalchemy import Column, String, Integer, ForeignKey, Text, BigInteger
from sqlalchemy.orm import relationship
from app.models.base import BaseModel

class Sequence(BaseModel):
    __tablename__ = 'sequences'
    
    # type = Column(String(16), nullable=False, default='sequence')
    code = Column(String(64), nullable=False)
    name = Column(String(64), nullable=False)
    
    frame_start = Column(Integer, nullable=True)
    frame_end = Column(Integer, nullable=True)
    
    template_id = Column(BigInteger, ForeignKey('templates.id'), nullable=True)
    domain_id = Column(BigInteger, ForeignKey('domains.id'), nullable=True)
    project_id = Column(BigInteger, ForeignKey('projects.id'), nullable=False)
    episode_id = Column(BigInteger, ForeignKey('episodes.id'), nullable=True)
    
    thumbnail_url = Column(String(256), nullable=True)
    description = Column(Text, nullable=True)
    tag = Column(String(64), nullable=True)
    
    # Relationships
    project = relationship('Project', back_populates='sequences')
    episode = relationship('Episode', back_populates='sequences')
    shots = relationship('Shot', back_populates='sequence')