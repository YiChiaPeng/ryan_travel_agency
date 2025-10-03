"""
個人資料服務
處理個人資料的 CRUD 操作和圖片上傳
"""
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from typing import Optional, Dict, Any
import base64
import hashlib
from ..models import Individual
from ..utils.db import SessionLocal


class IndividualService:
    """個人資料服務類"""
    
    @staticmethod
    def create_individual(individual_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        創建新的個人資料
        
        Args:
            individual_data: 包含個人資料的字典
            
        Returns:
            創建結果和個人資料 ID
        """
        db: Session = SessionLocal()
        try:
            # 處理圖片數據
            front_image_data = None
            back_image_data = None
            
            if 'id_card_front_image' in individual_data:
                front_image_data = IndividualService._process_image_data(
                    individual_data['id_card_front_image']
                )
            
            if 'id_card_back_image' in individual_data:
                back_image_data = IndividualService._process_image_data(
                    individual_data['id_card_back_image']
                )
            
            # 處理護照圖片數據
            passport_image_data = None
            if 'passport_infomation_image' in individual_data:
                passport_image_data = IndividualService._process_image_data(
                    individual_data['passport_infomation_image']
                )
            
            # 創建個人資料實例
            individual = Individual(
                chinese_last_name=individual_data.get('chinese_last_name'),
                chinese_first_name=individual_data.get('chinese_first_name'),
                english_last_name=individual_data.get('english_last_name'),
                english_first_name=individual_data.get('english_first_name'),
                national_id=individual_data.get('national_id'),
                gender=individual_data.get('gender'),
                passport_infomation_image=passport_image_data,
                id_card_front_image=front_image_data,
                id_card_back_image=back_image_data
            )
            
            db.add(individual)
            db.commit()
            db.refresh(individual)
            
            return {
                'success': True,
                'individual_id': individual.id,
                'message': '個人資料創建成功'
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
                'error': f'創建個人資料失敗: {str(e)}'
            }
        finally:
            db.close()
    
    @staticmethod
    def get_individual_by_id(individual_id: int) -> Optional[Dict[str, Any]]:
        """
        根據 ID 獲取個人資料
        
        Args:
            individual_id: 個人資料 ID
            
        Returns:
            個人資料字典或 None
        """
        db: Session = SessionLocal()
        try:
            individual = db.query(Individual).filter(Individual.id == individual_id).first()
            if not individual:
                return None
            
            return {
                'id': individual.id,
                'chinese_last_name': individual.chinese_last_name,
                'chinese_first_name': individual.chinese_first_name,
                'english_last_name': individual.english_last_name,
                'english_first_name': individual.english_first_name,
                'national_id': individual.national_id,
                'gender': individual.gender,
                'full_chinese_name': individual.full_chinese_name,
                'full_english_name': individual.full_english_name,
                'has_passport_image': individual.passport_infomation_image is not None,
                'has_front_image': individual.id_card_front_image is not None,
                'has_back_image': individual.id_card_back_image is not None,
                'created_at': individual.created_at.isoformat(),
                'updated_at': individual.updated_at.isoformat()
            }
            
        except Exception as e:
            return None
        finally:
            db.close()
    
    @staticmethod
    def find_individual_by_name(chinese_last_name: str, chinese_first_name: str) -> Optional[Dict[str, Any]]:
        """
        根據中文姓名查找個人資料
        
        Args:
            chinese_last_name: 中文姓
            chinese_first_name: 中文名
            
        Returns:
            個人資料字典或 None
        """
        db: Session = SessionLocal()
        try:
            individual = db.query(Individual).filter(
                Individual.chinese_last_name == chinese_last_name,
                Individual.chinese_first_name == chinese_first_name
            ).first()
            
            if not individual:
                return None
            
            return IndividualService.get_individual_by_id(individual.id)
            
        except Exception as e:
            return None
        finally:
            db.close()
    
    @staticmethod
    def update_individual(individual_id: int, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        更新個人資料
        
        Args:
            individual_id: 個人資料 ID
            update_data: 要更新的資料
            
        Returns:
            更新結果
        """
        db: Session = SessionLocal()
        try:
            individual = db.query(Individual).filter(Individual.id == individual_id).first()
            if not individual:
                return {
                    'success': False,
                    'error': '找不到該個人資料'
                }
            
            # 更新基本資料
            if 'chinese_last_name' in update_data:
                individual.chinese_last_name = update_data['chinese_last_name']
            if 'chinese_first_name' in update_data:
                individual.chinese_first_name = update_data['chinese_first_name']
            if 'english_last_name' in update_data:
                individual.english_last_name = update_data['english_last_name']
            if 'english_first_name' in update_data:
                individual.english_first_name = update_data['english_first_name']
            if 'national_id' in update_data:
                individual.national_id = update_data['national_id']
            if 'gender' in update_data:
                individual.gender = update_data['gender']
            
            # 更新圖片
            if 'passport_infomation_image' in update_data:
                individual.passport_infomation_image = IndividualService._process_image_data(
                    update_data['passport_infomation_image']
                )
            if 'id_card_front_image' in update_data:
                individual.id_card_front_image = IndividualService._process_image_data(
                    update_data['id_card_front_image']
                )
            if 'id_card_back_image' in update_data:
                individual.id_card_back_image = IndividualService._process_image_data(
                    update_data['id_card_back_image']
                )
            
            db.commit()
            db.refresh(individual)
            
            return {
                'success': True,
                'message': '個人資料更新成功'
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
                'error': f'更新個人資料失敗: {str(e)}'
            }
        finally:
            db.close()
    
    @staticmethod
    def get_individual_image(individual_id: int, image_type: str) -> Optional[bytes]:
        """
        獲取個人資料的圖片
        
        Args:
            individual_id: 個人資料 ID
            image_type: 圖片類型 ('front' 或 'back')
            
        Returns:
            圖片二進位數據或 None
        """
        db: Session = SessionLocal()
        try:
            individual = db.query(Individual).filter(Individual.id == individual_id).first()
            if not individual:
                return None
            
            if image_type == 'front':
                return individual.id_card_front_image
            elif image_type == 'back':
                return individual.id_card_back_image
            elif image_type == 'passport':
                return individual.passport_infomation_image
            else:
                return None
            
        except Exception as e:
            return None
        finally:
            db.close()
    
    @staticmethod
    def _process_image_data(image_data: Any) -> Optional[bytes]:
        """
        處理圖片數據，支援 base64 字符串或直接的 bytes
        
        Args:
            image_data: 圖片數據
            
        Returns:
            處理後的 bytes 數據
        """
        if image_data is None:
            return None
        
        if isinstance(image_data, str):
            # 假設是 base64 編碼的字符串
            try:
                # 移除可能的前綴 (data:image/jpeg;base64,)
                if ',' in image_data:
                    image_data = image_data.split(',')[1]
                return base64.b64decode(image_data)
            except Exception:
                return None
        elif isinstance(image_data, bytes):
            return image_data
        else:
            return None
    
    @staticmethod
    def create_or_update_individual(individual_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        創建或更新個人資料（根據姓名查找是否存在）
        
        Args:
            individual_data: 個人資料
            
        Returns:
            操作結果和個人資料 ID
        """
        chinese_last_name = individual_data.get('chinese_last_name')
        chinese_first_name = individual_data.get('chinese_first_name')
        
        if not chinese_last_name or not chinese_first_name:
            return {
                'success': False,
                'error': '中文姓名為必填項'
            }
        
        # 查找是否已存在
        existing = IndividualService.find_individual_by_name(
            chinese_last_name, chinese_first_name
        )
        
        if existing:
            # 更新現有資料
            result = IndividualService.update_individual(existing['id'], individual_data)
            if result['success']:
                result['individual_id'] = existing['id']
                result['action'] = 'updated'
            return result
        else:
            # 創建新資料
            result = IndividualService.create_individual(individual_data)
            if result['success']:
                result['action'] = 'created'
            return result