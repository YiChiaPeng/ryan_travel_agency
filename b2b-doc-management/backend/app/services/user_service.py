from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from werkzeug.security import generate_password_hash
from ..models import User
from ..utils.db import SessionLocal


class UserService:
    @staticmethod
    def list_users(page: int = 1, limit: int = 50) -> Dict[str, Any]:
        db: Session = SessionLocal()
        try:
            query = db.query(User)
            total = query.count()
            offset = (page - 1) * limit
            rows: List[User] = query.order_by(User.created_at.desc()).offset(offset).limit(limit).all()

            data = [
                {
                    'id': u.id,
                    'company_name': u.company_name,
                    'username': u.username,
                    'email': u.email,
                    'role': u.role,
                    'created_at': u.created_at.isoformat() if u.created_at else None,
                    'updated_at': u.updated_at.isoformat() if u.updated_at else None,
                }
                for u in rows
            ]

            return {
                'success': True,
                'data': data,
                'pagination': {
                    'page': page,
                    'limit': limit,
                    'total': total,
                    'pages': (total + limit - 1) // limit,
                },
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
        finally:
            db.close()

    @staticmethod
    def get_user(user_id: int) -> Optional[Dict[str, Any]]:
        db: Session = SessionLocal()
        try:
            u = db.query(User).filter(User.id == user_id).first()
            if not u:
                return None
            return {
                'id': u.id,
                'company_name': u.company_name,
                'username': u.username,
                'email': u.email,
                'role': u.role,
                'created_at': u.created_at.isoformat() if u.created_at else None,
                'updated_at': u.updated_at.isoformat() if u.updated_at else None,
            }
        except Exception:
            return None
        finally:
            db.close()

    @staticmethod
    def create_user(data: Dict[str, Any]) -> Dict[str, Any]:
        db: Session = SessionLocal()
        try:
            username = data.get('username')
            password = data.get('password')
            company_name = data.get('company_name') or data.get('company') or ''
            email = data.get('email') or f"{username}@example.com"
            role = data.get('role') or 'user'

            if not username or not password:
                return {'success': False, 'error': 'username 與 password 為必填'}

            hashed = generate_password_hash(password)
            user = User(
                username=username,
                password=hashed,
                company_name=company_name,
                email=email,
                role=role,
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            return {
                'success': True,
                'id': user.id,
                'message': '使用者建立成功',
            }
        except IntegrityError as e:
            db.rollback()
            return {'success': False, 'error': '使用者或信箱已存在'}
        except Exception as e:
            db.rollback()
            return {'success': False, 'error': str(e)}
        finally:
            db.close()

    @staticmethod
    def update_user(user_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
        db: Session = SessionLocal()
        try:
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                return {'success': False, 'error': '找不到使用者'}

            if 'username' in data and data['username']:
                user.username = data['username']
            if 'company_name' in data:
                user.company_name = data['company_name']
            if 'company' in data:
                user.company_name = data['company']
            if 'email' in data:
                user.email = data['email']
            if 'role' in data and data['role']:
                user.role = data['role']
            if 'password' in data and data['password']:
                user.password = generate_password_hash(data['password'])

            db.commit()
            return {'success': True, 'message': '使用者更新成功'}
        except IntegrityError:
            db.rollback()
            return {'success': False, 'error': '使用者或信箱已存在'}
        except Exception as e:
            db.rollback()
            return {'success': False, 'error': str(e)}
        finally:
            db.close()

    @staticmethod
    def delete_user(user_id: int) -> Dict[str, Any]:
        db: Session = SessionLocal()
        try:
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                return {'success': False, 'error': '找不到使用者'}
            db.delete(user)
            db.commit()
            return {'success': True, 'message': '使用者已刪除'}
        except Exception as e:
            db.rollback()
            return {'success': False, 'error': str(e)}
        finally:
            db.close()
