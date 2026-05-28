from sqlalchemy import Column, String, Index, Boolean, Table, ForeignKey, BigInteger
from sqlalchemy.orm import relationship
from app.models.base import BaseModel, Base

# Association Table for many-to-many project template to domain template relationship
template_domain_mappings = Table(
    'template_domain_mappings',
    Base.metadata,
    Column('project_template_id', BigInteger, ForeignKey('templates.id', ondelete='CASCADE'), primary_key=True),
    Column('domain_template_id', BigInteger, ForeignKey('templates.id', ondelete='CASCADE'), primary_key=True)
)

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

    # Many-to-many relationship: A project template has many domain templates
    domain_templates = relationship(
        'Template',
        secondary=template_domain_mappings,
        primaryjoin="Template.id==template_domain_mappings.c.project_template_id",
        secondaryjoin="Template.id==template_domain_mappings.c.domain_template_id",
        back_populates="project_templates",
        lazy="selectin"
    )

    # Many-to-many relationship: A domain template belongs to many project templates
    project_templates = relationship(
        'Template',
        secondary=template_domain_mappings,
        primaryjoin="Template.id==template_domain_mappings.c.domain_template_id",
        secondaryjoin="Template.id==template_domain_mappings.c.project_template_id",
        back_populates="domain_templates",
        lazy="selectin"
    )

    @property
    def applicable_templates(self) -> str:
        # Check if we have project_templates (this template is a domain template)
        if not self.project_templates:
            return ""
        return ",".join([t.code for t in self.project_templates])

    @applicable_templates.setter
    def applicable_templates(self, value):
        # Handled in CRUD layer, but setter provided to prevent attribute errors
        pass

    __table_args__ = (
        Index('ix_template_code', 'code'),
    )