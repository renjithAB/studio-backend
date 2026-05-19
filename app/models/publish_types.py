from sqlalchemy import BigInteger, Column, Text, String, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import BaseModel

class PublishType(BaseModel):
    __tablename__ = "publish_types"

    id              = Column(BigInteger, primary_key=True, index=True)
    project_id      = Column(BigInteger, ForeignKey('projects.id'), nullable=False)
    variant_id      = Column(BigInteger, ForeignKey('variants.id'), nullable=True)
    task_id         = Column(BigInteger, ForeignKey('tasks.id'), nullable=True)
    name            = Column(String(255), nullable=True)
    description     = Column(Text, nullable=True)
    code            = Column(Text, nullable=False)
    publish_type_code = Column(String(64), nullable=True)  # e.g. 'submit' or 'release'
