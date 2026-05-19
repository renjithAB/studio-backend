from sqlalchemy import Column, DateTime, Boolean, String, text, BigInteger
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()

class BaseModel(Base):
    __abstract__ = True
    
    id = Column(BigInteger, primary_key=True, index=True)
    is_active = Column(Boolean, nullable=False, default=True, server_default='true')
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(BigInteger, nullable=True)
    updated_by = Column(BigInteger, nullable=True)