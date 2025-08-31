from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from .utils.db import Base

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True)
    password = Column(String(128))
    is_admin = Column(Integer, default=0)
    company_name = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)

    documents = relationship("Document", back_populates="owner")

class Document(Base):
    __tablename__ = 'documents'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    document_type = Column(String(50))
    urgency = Column(String(20))
    submission_date = Column(DateTime, default=datetime.utcnow)
    customer_name = Column(String(100))
    file_path = Column(Text)
    status = Column(String(20), default='pending')
    rejection_reason = Column(Text, nullable=True)
    resubmission = Column(Text, nullable=True)

    owner = relationship("User", back_populates="documents")