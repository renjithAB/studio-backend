from sqlalchemy import Column, String, ForeignKey, Text, BigInteger
from sqlalchemy.orm import relationship
from app.models.base import BaseModel

class Library(BaseModel):
    __tablename__ = 'libraries'
    
    # type = Column(String(16), nullable=False, default='library')
    code = Column(String(64), nullable=False)
    name = Column(String(64), nullable=False)
    
    template_id = Column(BigInteger, ForeignKey('templates.id'), nullable=True)
    project_id = Column(BigInteger, ForeignKey('projects.id'), nullable=False)
    
    thumbnail_url = Column(String(256), nullable=True)
    description = Column(Text, nullable=True)
    tag = Column(String(64), nullable=True)
    
    # Relationships
    project = relationship('Project', back_populates='libraries')
    cycles = relationship('Cycle', back_populates='library')