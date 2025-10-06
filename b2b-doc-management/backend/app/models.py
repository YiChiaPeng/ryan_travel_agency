from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum, LargeBinary, Date
from sqlalchemy.orm import relationship
from datetime import datetime, date
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

    # 新的關聯
    applications = relationship("Application", back_populates="user")
    notifications = relationship("Notification", back_populates="user")
    
    # 舊的關聯（向後兼容）
    documents = relationship("Document", back_populates="owner")
    
    @property
    def is_admin(self):
        """檢查用戶是否為管理員"""
        return self.role in ['admin', 'sudo']

class Individual(Base):
    """個人資料模型"""
    __tablename__ = 'individuals'

    id = Column(Integer, primary_key=True, index=True)
    chinese_last_name = Column(String(100), nullable=False, comment='中文姓')
    chinese_first_name = Column(String(100), nullable=False, comment='中文名')
    english_last_name = Column(String(100), nullable=False, comment='英文姓')
    english_first_name = Column(String(100), nullable=False, comment='英文名')
    national_id = Column(String(20), nullable=False, unique=True, comment='身分證字號')
    gender = Column(Enum('男', '女'), nullable=False, comment='性別')
    passport_infomation_image = Column(LargeBinary, comment='護照資訊頁圖片')
    id_card_front_image = Column(LargeBinary, comment='身分證正面圖片')
    id_card_back_image = Column(LargeBinary, comment='身分證背面圖片')
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 關聯
    applications = relationship("Application", back_populates="individual")

    @property
    def full_chinese_name(self):
        """完整中文姓名"""
        return f"{self.chinese_last_name}{self.chinese_first_name}"
    
    @property
    def full_english_name(self):
        """完整英文姓名"""
        return f"{self.english_first_name} {self.english_last_name}"

class Application(Base):
    """申請案件模型"""
    __tablename__ = 'applications'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    individual_id = Column(Integer, ForeignKey('individuals.id'), nullable=False)
    application_type = Column(Enum('首次申請', '換證', '遺失件'), nullable=False)
    urgency = Column(Enum('急件', '普通件'), nullable=False)
    application_date = Column(Date, nullable=False, default=date.today)
    customer_name = Column(String(255), nullable=False)
    status = Column(Enum('草稿', '待審核', '補件', '送件中', '已完成'), default='草稿')
    substatus = Column(Enum('失敗', '成功', '補繳費用'), nullable=True)
    reason = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 關聯
    user = relationship("User", back_populates="applications")
    individual = relationship("Individual", back_populates="applications")

class Notification(Base):
    __tablename__ = 'notifications'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    message = Column(Text)
    is_read = Column(Integer, default=0)  # 使用 INTEGER 代替 BOOLEAN 以兼容 MariaDB
    created_at = Column(DateTime, default=datetime.utcnow)

    # 關聯
    user = relationship("User", back_populates="notifications")

# === 以下為舊模型，保持向後兼容 ===

class Document(Base):
    __tablename__ = 'documents'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    document_type = Column(Enum('首次申請', '換證', '遺失件'))
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