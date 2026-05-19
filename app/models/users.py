from sqlalchemy import Column, String, Boolean, JSON, DateTime, Text, ForeignKey, BigInteger
from sqlalchemy.orm import relationship
from app.models.base import BaseModel

class User(BaseModel):
    __tablename__ = 'users'
    
    type = Column(String(64), nullable=False, default='user')
    code = Column(String(64), nullable=True)
    first_name = Column(String(32), nullable=True)
    last_name = Column(String(32), nullable=True)
    email = Column(String(64), unique=True, nullable=False)
    phone = Column(String(20), nullable=True)
    timezone = Column(String(50), nullable=False, default='UTC')
    locale = Column(String(10), nullable=False, default='en_US')
    last_login_at = Column(DateTime(timezone=True), nullable=True)
    last_activity_at = Column(DateTime(timezone=True), nullable=True)
    
    role_id = Column(BigInteger, ForeignKey('templates.id'), nullable=True)
    permission_id = Column(BigInteger, ForeignKey('templates.id'), nullable=True)
    is_super = Column(Boolean, nullable=False, default=False)
    
    show_link = Column(JSON, nullable=True)
    private_key = Column(String(256), nullable=True)
    thumbnail_url = Column(String(256), nullable=True)
    description = Column(Text, nullable=True)
    tag = Column(String(64), nullable=True)
    
    preferences = Column(JSON, nullable=False, default={})
    
    synced_to_superadmin = Column(Boolean, nullable=False, default=False)
    superadmin_user_id = Column(String(36), nullable=True)  # Keep as String for external system ID
    last_synced_at = Column(DateTime(timezone=True), nullable=True)
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    is_deleted = Column(Boolean, nullable=False, default=False)
    
    # Relationships
    role = relationship('Template', foreign_keys=[role_id])
    permission = relationship('Template', foreign_keys=[permission_id])