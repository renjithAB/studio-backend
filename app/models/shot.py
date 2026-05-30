from sqlalchemy import Column, String, Integer, ForeignKey, Text, JSON, BigInteger
from sqlalchemy.orm import relationship
from app.models.base import BaseModel

class Shot(BaseModel):
    __tablename__ = 'shots'
    
    # type = Column(String(16), nullable=False, default='shot')
    code = Column(String(64), nullable=False)
    name = Column(String(64), nullable=False)
    
    frame_start = Column(Integer, nullable=True)
    frame_end = Column(Integer, nullable=True)
    cut_in = Column(Integer, nullable=True)
    cut_out = Column(Integer, nullable=True)
    
    asset_ids = Column(JSON, nullable=True)
    
    template_id = Column(BigInteger, ForeignKey('templates.id'), nullable=True)
    domain_id = Column(BigInteger, ForeignKey('domains.id'), nullable=True)
    project_id = Column(BigInteger, ForeignKey('projects.id'), nullable=False)
    episode_id = Column(BigInteger, ForeignKey('episodes.id'), nullable=True)
    sequence_id = Column(BigInteger, ForeignKey('sequences.id'), nullable=False)
    
    thumbnail_url = Column(String(256), nullable=True)
    description = Column(Text, nullable=True)
    tag = Column(String(64), nullable=True)
    
    # Relationships
    project = relationship('Project', back_populates='shots')
    sequence = relationship('Sequence', back_populates='shots')
    shotsets = relationship('Shotset', back_populates='shot')