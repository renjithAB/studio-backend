# app/models/template.py

from sqlalchemy import Column, String, Index, Boolean
from sqlalchemy.orm import relationship
from app.models.base import BaseModel

class Template(BaseModel):
    __tablename__ = 'templates'

    code = Column(String(64), unique=True, nullable=False)   # e.g., "film_template", "animation_template"
    name = Column(String(256), nullable=False)
    description = Column(String(512), nullable=True)
    thumbnail_url = Column(String(512), nullable=True)
    tag = Column(String(64), nullable=True)
    has_episode = Column(Boolean, nullable=False)

    # Relationships
    projects = relationship('Project', back_populates='template')

    __table_args__ = (
        Index('ix_template_code', 'code'),
    )