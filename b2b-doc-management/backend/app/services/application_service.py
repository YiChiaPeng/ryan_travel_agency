"""
申請案件服務
處理申請案件的 CRUD 操作和業務邏輯
"""
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from typing import Optional, Dict, Any, List
from datetime import date, datetime
from ..models import Application, Individual, User
from ..utils.db import SessionLocal
from .individual_service import IndividualService


class ApplicationService:
    """申請案件服務類"""
    
    @staticmethod
    def create_application(application_data: Dict[str, Any], user_id: int) -> Dict[str, Any]:
        """
        創建新的申請案件
        
        Args:
            application_data: 包含申請案件資料的字典
            user_id: 申請用戶的 ID
            
        Returns:
            創建結果和申請案件 ID
        """
        db: Session = SessionLocal()
        try:
            # 處理個人資料
            individual_data = application_data.get('individual_data', {})
            individual_result = IndividualService.create_or_update_individual(individual_data)
            
            if not individual_result['success']:
                return {
                    'success': False,
                    'error': f"個人資料處理失敗: {individual_result['error']}"
                }
            
            individual_id = individual_result['individual_id']
            
            # 創建申請案件
            application = Application(
                user_id=user_id,
                individual_id=individual_id,
                application_type=application_data.get('application_type'),
                urgency=application_data.get('urgency'),
                application_date=ApplicationService._parse_date(
                    application_data.get('application_date')
                ),
                customer_name=application_data.get('customer_name'),
                status=application_data.get('status', '草稿'),
                substatus=application_data.get('substatus'),
                reason=application_data.get('reason')
            )
            
            db.add(application)
            db.commit()
            db.refresh(application)
            
            return {
                'success': True,
                'application_id': application.id,
                'individual_id': individual_id,
                'individual_action': individual_result.get('action', 'unknown'),
                'message': '申請案件創建成功'
            }
            
        except SQLAlchemyError as e:
            db.rollback()
            return {
                'success': False,
                'error': f'資料庫錯誤: {str(e)}'
            }
        except Exception as e:
            db.rollback()
            return {
                'success': False,
                'error': f'創建申請案件失敗: {str(e)}'
            }
        finally:
            db.close()
    
    @staticmethod
    def get_application_by_id(application_id: int, user_id: Optional[int] = None) -> Optional[Dict[str, Any]]:
        """
        根據 ID 獲取申請案件詳情
        
        Args:
            application_id: 申請案件 ID
            user_id: 用戶 ID（用於權限檢查，None 表示管理員查看）
            
        Returns:
            申請案件詳情字典或 None
        """
        db: Session = SessionLocal()
        try:
            query = db.query(Application).filter(Application.id == application_id)
            
            # 如果指定了 user_id，則只能查看自己的申請
            if user_id is not None:
                query = query.filter(Application.user_id == user_id)
            
            application = query.first()
            if not application:
                return None
            
            # 獲取關聯的個人資料
            individual_data = IndividualService.get_individual_by_id(application.individual_id)
            
            # 獲取用戶資料
            user = db.query(User).filter(User.id == application.user_id).first()
            
            return {
                'id': application.id,
                'user_id': application.user_id,
                'individual_id': application.individual_id,
                'application_type': application.application_type,
                'urgency': application.urgency,
                'application_date': application.application_date.isoformat() if application.application_date else None,
                'customer_name': application.customer_name,
                'status': application.status,
                'substatus': application.substatus,
                'reason': application.reason,
                'created_at': application.created_at.isoformat(),
                'updated_at': application.updated_at.isoformat(),
                'individual_data': individual_data,
                'user_data': {
                    'id': user.id,
                    'company_name': user.company_name,
                    'username': user.username,
                    'email': user.email
                } if user else None
            }
            
        except Exception as e:
            return None
        finally:
            db.close()
    
    @staticmethod
    def get_applications_by_user(user_id: int, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        獲取用戶的申請案件列表
        
        Args:
            user_id: 用戶 ID
            status: 狀態篩選（可選）
            
        Returns:
            申請案件列表
        """
        db: Session = SessionLocal()
        try:
            query = db.query(Application).filter(Application.user_id == user_id)
            
            if status:
                query = query.filter(Application.status == status)
            
            applications = query.order_by(Application.created_at.desc()).all()
            
            result = []
            for app in applications:
                individual_data = IndividualService.get_individual_by_id(app.individual_id)
                result.append({
                    'id': app.id,
                    'application_type': app.application_type,
                    'urgency': app.urgency,
                    'application_date': app.application_date.isoformat() if app.application_date else None,
                    'customer_name': app.customer_name,
                    'status': app.status,
                    'substatus': app.substatus,
                    'created_at': app.created_at.isoformat(),
                    'individual_name': individual_data['full_chinese_name'] if individual_data else None
                })
            
            return result
            
        except Exception as e:
            return []
        finally:
            db.close()
    
    @staticmethod
    def update_application(application_id: int, update_data: Dict[str, Any], user_id: Optional[int] = None) -> Dict[str, Any]:
        """
        更新申請案件
        
        Args:
            application_id: 申請案件 ID
            update_data: 要更新的資料
            user_id: 用戶 ID（用於權限檢查，None 表示管理員操作）
            
        Returns:
            更新結果
        """
        db: Session = SessionLocal()
        try:
            query = db.query(Application).filter(Application.id == application_id)
            
            # 如果指定了 user_id，則只能更新自己的申請
            if user_id is not None:
                query = query.filter(Application.user_id == user_id)
            
            application = query.first()
            if not application:
                return {
                    'success': False,
                    'error': '找不到該申請案件或無權限操作'
                }
            
            # 更新申請案件資料
            if 'application_type' in update_data:
                application.application_type = update_data['application_type']
            if 'urgency' in update_data:
                application.urgency = update_data['urgency']
            if 'application_date' in update_data:
                application.application_date = ApplicationService._parse_date(
                    update_data['application_date']
                )
            if 'customer_name' in update_data:
                application.customer_name = update_data['customer_name']
            if 'status' in update_data:
                application.status = update_data['status']
            if 'substatus' in update_data:
                application.substatus = update_data['substatus']
            if 'reason' in update_data:
                application.reason = update_data['reason']
            
            # 如果有個人資料更新
            if 'individual_data' in update_data:
                individual_result = IndividualService.update_individual(
                    application.individual_id, 
                    update_data['individual_data']
                )
                if not individual_result['success']:
                    return {
                        'success': False,
                        'error': f"個人資料更新失敗: {individual_result['error']}"
                    }
            
            db.commit()
            db.refresh(application)
            
            return {
                'success': True,
                'message': '申請案件更新成功'
            }
            
        except SQLAlchemyError as e:
            db.rollback()
            return {
                'success': False,
                'error': f'資料庫錯誤: {str(e)}'
            }
        except Exception as e:
            db.rollback()
            return {
                'success': False,
                'error': f'更新申請案件失敗: {str(e)}'
            }
        finally:
            db.close()
    
    @staticmethod
    def delete_application(application_id: int, user_id: Optional[int] = None) -> Dict[str, Any]:
        """
        刪除申請案件
        
        Args:
            application_id: 申請案件 ID
            user_id: 用戶 ID（用於權限檢查，None 表示管理員操作）
            
        Returns:
            刪除結果
        """
        db: Session = SessionLocal()
        try:
            query = db.query(Application).filter(Application.id == application_id)
            
            # 如果指定了 user_id，則只能刪除自己的申請
            if user_id is not None:
                query = query.filter(Application.user_id == user_id)
            
            application = query.first()
            if not application:
                return {
                    'success': False,
                    'error': '找不到該申請案件或無權限操作'
                }
            
            db.delete(application)
            db.commit()
            
            return {
                'success': True,
                'message': '申請案件刪除成功'
            }
            
        except SQLAlchemyError as e:
            db.rollback()
            return {
                'success': False,
                'error': f'資料庫錯誤: {str(e)}'
            }
        except Exception as e:
            db.rollback()
            return {
                'success': False,
                'error': f'刪除申請案件失敗: {str(e)}'
            }
        finally:
            db.close()
    
    @staticmethod
    def get_all_applications(status: Optional[str] = None, page: int = 1, limit: int = 50) -> Dict[str, Any]:
        """
        獲取所有申請案件（管理員用）
        
        Args:
            status: 狀態篩選（可選）
            page: 頁碼
            limit: 每頁數量
            
        Returns:
            申請案件列表和分頁資訊
        """
        db: Session = SessionLocal()
        try:
            query = db.query(Application)
            
            if status:
                query = query.filter(Application.status == status)
            
            # 計算總數
            total = query.count()
            
            # 分頁
            offset = (page - 1) * limit
            applications = query.order_by(Application.created_at.desc()).offset(offset).limit(limit).all()
            
            result = []
            for app in applications:
                individual_data = IndividualService.get_individual_by_id(app.individual_id)
                user = db.query(User).filter(User.id == app.user_id).first()
                
                result.append({
                    'id': app.id,
                    'application_type': app.application_type,
                    'urgency': app.urgency,
                    'application_date': app.application_date.isoformat() if app.application_date else None,
                    'customer_name': app.customer_name,
                    'status': app.status,
                    'substatus': app.substatus,
                    'created_at': app.created_at.isoformat(),
                    'individual_name': individual_data['full_chinese_name'] if individual_data else None,
                    'company_name': user.company_name if user else None
                })
            
            return {
                'success': True,
                'data': result,
                'pagination': {
                    'page': page,
                    'limit': limit,
                    'total': total,
                    'pages': (total + limit - 1) // limit
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'獲取申請案件列表失敗: {str(e)}'
            }
        finally:
            db.close()
    
    @staticmethod
    def _parse_date(date_value: Any) -> Optional[date]:
        """
        解析日期值
        
        Args:
            date_value: 日期值（字符串、日期對象或 None）
            
        Returns:
            日期對象或 None
        """
        if date_value is None:
            return None
        
        if isinstance(date_value, date):
            return date_value
        
        if isinstance(date_value, str):
            try:
                # 嘗試解析 ISO 格式日期
                return datetime.fromisoformat(date_value.replace('Z', '+00:00')).date()
            except ValueError:
                try:
                    # 嘗試解析其他格式
                    return datetime.strptime(date_value, '%Y-%m-%d').date()
                except ValueError:
                    return None
        
        return None