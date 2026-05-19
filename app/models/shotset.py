from sqlalchemy import Column, String, ForeignKey, Text, BigInteger
from sqlalchemy.orm import relationship
from app.models.base import BaseModel

class Shotset(BaseModel):
    __tablename__ = 'shotsets'
    
    # type = Column(String(16), nullable=False, default='shotset')
    code = Column(String(64), nullable=True)
    name = Column(String(64), nullable=True)
    
    template_id = Column(BigInteger, ForeignKey('templates.id'), nullable=True)
    project_id = Column(BigInteger, ForeignKey('projects.id'), nullable=False)
    episode_id = Column(BigInteger, ForeignKey('episodes.id'), nullable=True)
    sequence_id = Column(BigInteger, ForeignKey('sequences.id'), nullable=True)
    shot_id = Column(BigInteger, ForeignKey('shots.id'), nullable=False)
    asset_id = Column(BigInteger, ForeignKey('assets.id'), nullable=False)
    
    thumbnail_url = Column(String(256), nullable=True)
    description = Column(Text, nullable=True)
    tag = Column(String(64), nullable=True)
    
    # Relationships
    project = relationship('Project', back_populates='shotsets')
    shot = relationship('Shot', back_populates='shotsets')
    asset = relationship('Asset', back_populates='shotsets')