from sqlalchemy import Column, String
from app.models.base import BaseModel

class Permission(BaseModel):
    __tablename__ = 'permissions'

    code = Column(String(64), unique=True, nullable=False)
    name = Column(String(256), nullable=False)
    description = Column(String(512), nullable=True)
