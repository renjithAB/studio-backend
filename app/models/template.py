from sqlalchemy import Column, String, Index, Boolean, Table, ForeignKey, BigInteger
from sqlalchemy.orm import relationship
from app.models.base import BaseModel, Base



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