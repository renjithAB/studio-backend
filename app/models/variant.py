from sqlalchemy import Column, String, ForeignKey, Text, BigInteger, Numeric
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy import Enum as PgEnum
from sqlalchemy.orm import relationship
from app.models.base import BaseModel
import enum

class PriorityEnum(str, enum.Enum):
    not_yet_started = "not_yet_started"
    work_in_progress = "work_in_progress"
    review = "review"
    approved = "approved"
    client_approved = "client_approved"

class StatusEnum(str, enum.Enum):
    below_normal = "below_normal"
    normal = "normal"
    above_normal = "above_normal"
    high = "high"
    critical = "critical"

class Variant(BaseModel):
    __tablename__ = 'variants'
    
    # type = Column(String(16), nullable=False, default='variant')
    code = Column(String(64), nullable=False)
    name = Column(String(64), nullable=False)
    
    template_id = Column(BigInteger, ForeignKey('templates.id'), nullable=True)
    project_id = Column(BigInteger, ForeignKey('projects.id'), nullable=False)
    asset_id = Column(BigInteger, ForeignKey('assets.id'), nullable=False)
    category_id = Column(BigInteger, ForeignKey('templates.id'), nullable=True)
    task_id = Column(BigInteger, ForeignKey('tasks.id', ondelete='CASCADE'), nullable=True)
    
    thumbnail_url = Column(String(256), nullable=True)
    description = Column(Text, nullable=True)
    tag = Column(String(64), nullable=True)

    # Pipeline tracking fields
    man_days    = Column(Numeric(6, 1), nullable=True)
    start_at    = Column(TIMESTAMP(timezone=True), nullable=True)
    end_at      = Column(TIMESTAMP(timezone=True), nullable=True)
    priority    = Column(PgEnum(PriorityEnum, name='priority_enum', create_type=False), nullable=True)
    assigned_by = Column(BigInteger, ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    review_by   = Column(BigInteger, ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    status      = Column(PgEnum(StatusEnum, name='status_enum', create_type=False), nullable=True)
    
    # Relationships
    project = relationship('Project', back_populates='variants')
    asset = relationship('Asset', back_populates='variants')
    assigned_by_user = relationship('User', foreign_keys=[assigned_by], lazy='select')
    review_by_user   = relationship('User', foreign_keys=[review_by],   lazy='select')