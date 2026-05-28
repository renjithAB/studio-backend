from sqlalchemy import Column, String, Boolean, Table, ForeignKey, BigInteger
from sqlalchemy.orm import relationship
from app.models.base import BaseModel, Base

# Many-to-many relationship table between Role and Permission
role_permissions = Table(
    'role_permissions',
    Base.metadata,
    Column('role_id', BigInteger, ForeignKey('roles.id', ondelete='CASCADE'), primary_key=True),
    Column('permission_id', BigInteger, ForeignKey('permissions.id', ondelete='CASCADE'), primary_key=True)
)

class Role(BaseModel):
    __tablename__ = 'roles'

    code = Column(String(64), unique=True, nullable=False)
    name = Column(String(256), nullable=False)
    description = Column(String(512), nullable=True)

    # Many-to-many relationship: A Role has many Permissions
    permissions = relationship(
        'Permission',
        secondary=role_permissions,
        backref='roles',
        lazy='selectin'
    )
