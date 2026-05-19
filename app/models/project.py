from sqlalchemy import Column, String, ForeignKey, Text, BigInteger, Index
from sqlalchemy.orm import relationship
from app.models.base import BaseModel

from app.models.template import Template
from app.models.domain import Domain
from app.models.category import Category

class Project(BaseModel):
    __tablename__ = 'projects'
    
    code = Column(String(64), unique=True, nullable=False)
    name = Column(String(64), nullable=False)
    description = Column(Text, nullable=True)
    thumbnail_url = Column(String(256), nullable=True)
    tag = Column(String(64), nullable=True)
    
    template_id = Column(BigInteger, ForeignKey('templates.id'), nullable=True)
    
    # Relationships
    template = relationship('Template')
    domains = relationship('Domain', back_populates='project', cascade='all, delete-orphan')
    categories = relationship('Category', back_populates='project', cascade='all, delete-orphan')
    episodes = relationship('Episode', back_populates='project')
    sequences = relationship('Sequence', back_populates='project')
    shots = relationship('Shot', back_populates='project')
    assets = relationship('Asset', back_populates='project')
    variants = relationship('Variant', back_populates='project')
    editorials = relationship('Editorial', back_populates='project')
    libraries = relationship('Library', back_populates='project')
    cycles = relationship('Cycle', back_populates='project')
    shotsets = relationship('Shotset', back_populates='project')
    
    __table_args__ = (
        Index('ix_project_code', 'code'),
        Index('ix_project_template_id', 'template_id'),
    )