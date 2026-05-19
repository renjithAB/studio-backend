# app/models/category.py

from sqlalchemy import Column, String, Integer, ForeignKey, Index, UniqueConstraint
from sqlalchemy.orm import relationship
from app.models.base import BaseModel

class Category(BaseModel):
    """
    Represents a category within a domain (e.g., Camera, Character under Asset domain).
    Categories are project‑specific and contain assets, tasks, etc.
    """
    __tablename__ = 'categories'

    code = Column(String(64), nullable=False)          # e.g., "CAMERA", "CHARACTER"
    name = Column(String(256), nullable=False)         # e.g., "Camera", "Character"
    description = Column(String(512), nullable=True)
    tag = Column(String(64), nullable=True)
    thumbnail_url = Column(String(256), nullable=True)

    # Foreign keys
    domain_id = Column(Integer, ForeignKey('domains.id'), nullable=False)
    project_id = Column(Integer, ForeignKey('projects.id'), nullable=False)  # denormalized for direct queries

    # Relationships
    domain = relationship('Domain', back_populates='categories')
    project = relationship('Project', back_populates='categories')
    # Add relationships to child tables later (e.g., assets, tasks)
    # assets = relationship('Asset', back_populates='category')  # if Asset model exists
    # tasks = relationship('Task', back_populates='category')  # if Task model exists

    __table_args__ = (
        # Ensure unique category codes within a project
        UniqueConstraint('project_id', 'code', name='uq_category_project_code'),
        # Indexes for faster queries
        Index('ix_category_domain_id', 'domain_id'),
        Index('ix_category_project_id', 'project_id'),
        Index('ix_category_code', 'code'),
    )