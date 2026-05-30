from sqlalchemy import Column, String, ForeignKey, Text, BigInteger
from sqlalchemy.orm import relationship
from app.models.base import BaseModel

class Episode(BaseModel):
    __tablename__ = 'episodes'
    
    # type = Column(String(16), nullable=False, default='episode')
    code = Column(String(64), nullable=False)
    name = Column(String(64), nullable=False)
    
    template_id = Column(BigInteger, ForeignKey('templates.id'), nullable=True)
    domain_id = Column(BigInteger, ForeignKey('domains.id'), nullable=True)
    project_id = Column(BigInteger, ForeignKey('projects.id'), nullable=False)

    
    thumbnail_url = Column(String(256), nullable=True)
    description = Column(Text, nullable=True)
    tag = Column(String(64), nullable=True)
    
    # Relationships
    project = relationship('Project', back_populates='episodes')
    sequences = relationship('Sequence', back_populates='episode')
    editorials = relationship('Editorial', back_populates='episode')
    