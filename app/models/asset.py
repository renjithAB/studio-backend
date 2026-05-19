from sqlalchemy import Column, String, ForeignKey, Text, BigInteger
from sqlalchemy.orm import relationship
from app.models.base import BaseModel

class Asset(BaseModel):
    __tablename__ = 'assets'
    
    id = Column(BigInteger, primary_key=True, index=True)
    # type = Column(String(16), nullable=False, default='asset')
    code = Column(String(64), nullable=False)
    name = Column(String(64), nullable=False)
    
    template_id = Column(BigInteger, ForeignKey('templates.id'), nullable=True)
    project_id = Column(BigInteger, ForeignKey('projects.id'), nullable=False)
    category_id = Column(BigInteger, ForeignKey('templates.id'), nullable=True)
    
    thumbnail_url = Column(String(256), nullable=True)
    description = Column(Text, nullable=True)
    tag = Column(String(64), nullable=True)
    
    # Relationships
    project = relationship('Project', back_populates='assets')
    variants = relationship('Variant', back_populates='asset')
    shotsets = relationship('Shotset', back_populates='asset')