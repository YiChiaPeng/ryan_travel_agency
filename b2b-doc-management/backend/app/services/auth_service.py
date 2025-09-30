import jwt
import datetime
from werkzeug.security import check_password_hash, generate_password_hash
from app.utils.db import SessionLocal
from app.models import User
from typing import Optional, Dict, Any

SECRET_KEY = 'replace-with-secure-secret'


class AuthService:
    def __init__(self):
        self.db = SessionLocal()

    def __del__(self):
        """確保資料庫連接被正確關閉"""
        if hasattr(self, 'db'):
            self.db.close()

    def login(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        """用戶登入
        
        Args:
            username: 用戶名
            password: 密碼
            
        Returns:
            成功返回用戶信息和token，失敗返回None
        """
        try:
            user = self.db.query(User).filter(User.username == username).first()
            if not user:
                return None

            if check_password_hash(user.password, password):
                payload = {
                    'sub': user.id,
                    'username': user.username,
                    'company': user.company_name,
                    'role': user.role,
                    'is_admin': user.is_admin,
                    'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=8)
                }
                token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
                return {
                    'id': user.id, 
                    'username': user.username, 
                    'company': user.company_name,
                    'role': user.role,
                    'is_admin': user.is_admin,
                    'token': token
                }
            return None
        except Exception as e:
            print(f"Login error: {e}")
            return None

    def register(self, username: str, password: str, company: str = '', email: str = '') -> Optional[Dict[str, Any]]:
        """用戶註冊
        
        Args:
            username: 用戶名
            password: 密碼
            company: 公司名稱
            email: 電子郵件
            
        Returns:
            成功返回用戶信息和token，失敗返回None
        """
        try:
            # 檢查用戶是否已存在
            existing_user = self.db.query(User).filter(User.username == username).first()
            if existing_user:
                return None
            
            # 創建新用戶
            hashed_password = generate_password_hash(password)
            new_user = User(
                username=username,
                password=hashed_password,
                company_name=company,
                email=email or f"{username}@example.com",
                role='user'  # 新用戶默認為普通用戶
            )
            
            self.db.add(new_user)
            self.db.commit()
            self.db.refresh(new_user)
            
            # 生成token
            payload = {
                'sub': new_user.id,
                'username': new_user.username,
                'company': new_user.company_name,
                'role': new_user.role,
                'is_admin': new_user.is_admin,
                'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=8)
            }
            token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
            
            return {
                'id': new_user.id,
                'username': new_user.username,
                'company': new_user.company_name,
                'role': new_user.role,
                'is_admin': new_user.is_admin,
                'token': token
            }
        except Exception as e:
            self.db.rollback()
            print(f"Registration error: {e}")
            return None

    def change_password(self, username: str, old_password: str, new_password: str) -> bool:
        """修改密碼
        
        Args:
            username: 用戶名
            old_password: 舊密碼
            new_password: 新密碼
            
        Returns:
            成功返回True，失敗返回False
        """
        try:
            user = self.db.query(User).filter(User.username == username).first()
            if not user:
                return False
            
            # 驗證舊密碼
            if not check_password_hash(user.password, old_password):
                return False
            
            # 更新密碼
            user.password = generate_password_hash(new_password)
            self.db.commit()
            return True
        except Exception as e:
            self.db.rollback()
            print(f"Change password error: {e}")
            return False

    def validate_token(self, token: str) -> Optional[Dict[str, Any]]:
        """驗證JWT token
        
        Args:
            token: JWT token
            
        Returns:
            有效返回token payload，無效返回None
        """
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            return payload
        except jwt.ExpiredSignatureError:
            print("Token has expired")
            return None
        except jwt.InvalidTokenError:
            print("Invalid token")
            return None

    def refresh_token(self, token: str) -> Optional[str]:
        """刷新token
        
        Args:
            token: 舊的JWT token
            
        Returns:
            成功返回新token，失敗返回None
        """
        try:
            # 驗證舊token（允許過期的token進行刷新）
            payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'], options={"verify_exp": False})
            
            # 檢查用戶是否還存在
            user = self.db.query(User).filter(User.id == payload['sub']).first()
            if not user:
                return None
            
            # 生成新token
            new_payload = {
                'sub': user.id,
                'username': user.username,
                'company': user.company_name,
                'role': user.role,
                'is_admin': user.is_admin,
                'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=8)
            }
            new_token = jwt.encode(new_payload, SECRET_KEY, algorithm='HS256')
            return new_token
        except Exception as e:
            print(f"Refresh token error: {e}")
            return None

    def logout(self, token: str) -> bool:
        """用戶登出（這裡可以實現token黑名單機制）
        
        Args:
            token: JWT token
            
        Returns:
            成功返回True
        """
        # 在真實應用中，可以將token加入黑名單
        # 或者實現其他登出邏輯
        return True

    def get_user_by_token(self, token: str) -> Optional[User]:
        """根據token獲取用戶信息
        
        Args:
            token: JWT token
            
        Returns:
            成功返回用戶對象，失敗返回None
        """
        payload = self.validate_token(token)
        if not payload:
            return None
        
        try:
            user = self.db.query(User).filter(User.id == payload['sub']).first()
            return user
        except Exception as e:
            print(f"Get user by token error: {e}")
            return None
