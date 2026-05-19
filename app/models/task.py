from sqlalchemy import Column, String, Integer, ForeignKey, Text, Boolean, DateTime, BigInteger
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from app.models.base import BaseModel

class Task(BaseModel):
    __tablename__ = 'tasks'
    
    # type = Column(String(16), nullable=False, default='task')
    code = Column(String(64), nullable=False)
    name = Column(String(64), nullable=False)
    
    template_id = Column(BigInteger, ForeignKey('templates.id'), nullable=True)
    project_id = Column(BigInteger, ForeignKey('projects.id'), nullable=False)
    
    asset_id = Column(BigInteger, ForeignKey('assets.id'), nullable=True)
    category_id = Column(BigInteger, ForeignKey('templates.id'), nullable=True)
    # variant_id = Column(BigInteger, ForeignKey('variants.id'), nullable=True)
    
    episode_id = Column(BigInteger, ForeignKey('episodes.id'), nullable=True)
    editorial_id = Column(BigInteger, ForeignKey('editorials.id'), nullable=True)
    sequence_id = Column(BigInteger, ForeignKey('sequences.id'), nullable=True)
    shot_id = Column(BigInteger, ForeignKey('shots.id'), nullable=True)
    
    library_id = Column(BigInteger, ForeignKey('libraries.id'), nullable=True)
    cycle_id = Column(BigInteger, ForeignKey('cycles.id'), nullable=True)
    
    thumbnail_url = Column(String(256), nullable=True)
    description = Column(Text, nullable=True)
    tag = Column(String(64), nullable=True)
    
    # due_date = Column(DateTime(timezone=True), nullable=True)
    # start_date = Column(DateTime(timezone=True), nullable=True)
    # completed_date = Column(DateTime(timezone=True), nullable=True)
    # status = Column(String(32), nullable=False, default='pending')
    # priority = Column(Integer, nullable=False, default=0)
    # progress = Column(Integer, nullable=False, default=0)
    
    # assignee_id = Column(BigInteger, ForeignKey('users.id'), nullable=True)
    # reviewer_id = Column(BigInteger, ForeignKey('users.id'), nullable=True)
    
    # task_metadata = Column(JSONB, nullable=True, default={})
    
    # parent_task_id = Column(BigInteger, ForeignKey('tasks.id'), nullable=True)
    
    # Relationships
    project = relationship('Project')
    asset = relationship('Asset')
    # variant = relationship('Variant')
    episode = relationship('Episode')
    editorial = relationship('Editorial')
    sequence = relationship('Sequence')
    shot = relationship('Shot')
    library = relationship('Library')
    cycle = relationship('Cycle')
    
    # assignee = relationship('User', foreign_keys=[assignee_id])
    # reviewer = relationship('User', foreign_keys=[reviewer_id])
    
    # parent_task = relationship('Task', remote_side='Task.id', foreign_keys=[parent_task_id], backref='subtasks')