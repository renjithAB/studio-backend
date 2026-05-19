# app/models/domain.py

from sqlalchemy import Column, String, Integer, ForeignKey, Index, UniqueConstraint, Enum
from sqlalchemy.orm import relationship
from app.models.base import BaseModel
import enum

class DomainTypeEnum(str, enum.Enum):
    # Change keys to lowercase to match the DB strings exactly
    asset = 'asset'
    editorial = 'editorial'
    episode = 'episode'
    library = 'library'
    cycle = 'cycle'

class Domain(BaseModel):
    """
    Represents a top‑level work area within a project (e.g., Episode, Asset, Library).
    Domains are project‑specific and contain categories.
    """
    __tablename__ = 'domains'

    code = Column(String(64), nullable=False)          # e.g., "EPISODE", "ASSET"
    name = Column(String(256), nullable=False)         # e.g., "Episode", "Asset"
    description = Column(String(512), nullable=True)
    tag = Column(String(64), nullable=True)
    thumbnail_url = Column(String(256), nullable=True)
    domain_type = Column(Enum(DomainTypeEnum, name="domain_type_enum", create_type=False), nullable=True)

    # Foreign key to the parent project
    project_id = Column(Integer, ForeignKey('projects.id'), nullable=False)

    # Relationships
    project = relationship('Project', back_populates='domains')
    categories = relationship('Category', back_populates='domain', cascade='all, delete-orphan')

    __table_args__ = (
        # Ensure unique domain codes within a project
        UniqueConstraint('project_id', 'code', name='uq_domain_project_code'),
        # Indexes for faster queries
        Index('ix_domain_project_id', 'project_id'),
        Index('ix_domain_code', 'code'),
    )