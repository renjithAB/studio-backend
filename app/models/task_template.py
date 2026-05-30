from sqlalchemy import Column, String, Index, Boolean, Table, ForeignKey, BigInteger, Enum
from sqlalchemy.orm import relationship
import enum
from typing import List
from app.models.base import BaseModel, Base

class TaskDomainEnum(str, enum.Enum):
    editorial = "editorial"
    asset = "asset"
    shot = "shot"
    sequence = "sequence"
    library = "library"
    cycle = "cycle"

# Association table for many-to-many relationship
task_template_project_mappings = Table(
    'task_template_project_mappings',
    Base.metadata,
    Column('task_template_id', BigInteger, ForeignKey('task_templates.id', ondelete='CASCADE'), primary_key=True),
    Column('project_template_id', BigInteger, ForeignKey('templates.id', ondelete='CASCADE'), primary_key=True)
)

class TaskTemplate(BaseModel):
    __tablename__ = 'task_templates'

    code = Column(String(64), unique=True, nullable=False)
    name = Column(String(256), nullable=False)
    description = Column(String(512), nullable=True)
    domain_code = Column(Enum(TaskDomainEnum, name='task_domain_enum'), nullable=False)

    # Many-to-many relationship
    project_templates = relationship(
        'Template',
        secondary=task_template_project_mappings,
        backref='task_templates',
        lazy='selectin'
    )

    @property
    def applies_to_templates(self) -> List[str]:
        return [t.code for t in self.project_templates]

    __table_args__ = (
        Index('ix_task_templates_code', 'code'),
    )
