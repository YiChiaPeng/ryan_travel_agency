from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
from .utils.db import Base

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    company_name = Column(String(255), unique=True, index=True)
    username = Column(String(255), unique=True, index=True)
    password = Column(String(255))
    email = Column(String(255), unique=True)
    role = Column(Enum('user', 'reviewer', 'admin', 'sudo'), default='user')
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    documents = relationship("Document", back_populates="owner")
    
    @property
    def is_admin(self):
        """檢查用戶是否為管理員"""
        return self.role in ['admin', 'sudo']

class Document(Base):
    __tablename__ = 'documents'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    document_type = Column(Enum('首來族', '換證', '遺失件'))
    urgency = Column(Enum('急件', '普通件'))
    application_date = Column(DateTime)
    customer_name = Column(String(255))
    status = Column(Enum('待審核', '退件', '已完成'), default='待審核')
    rejection_reason = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 為了兼容舊的欄位名稱
    @property
    def submission_date(self):
        return self.application_date
    
    @submission_date.setter
    def submission_date(self, value):
        self.application_date = value
    
    # 兼容舊的 file_path 和 resubmission 欄位
    file_path = Column(Text, nullable=True)
    resubmission = Column(Text, nullable=True)

    owner = relationship("User", back_populates="documents")

class Upload(Base):
    __tablename__ = 'uploads'

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey('documents.id'))
    file_path = Column(String(255))
    uploaded_at = Column(DateTime, default=datetime.utcnow)

class Notification(Base):
    __tablename__ = 'notifications'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    message = Column(Text)
    is_read = Column(Integer, default=0)  # 使用 INTEGER 代替 BOOLEAN 以兼容 MariaDB
    created_at = Column(DateTime, default=datetime.utcnow)