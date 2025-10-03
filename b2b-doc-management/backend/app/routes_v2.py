"""
新的 API 路由
處理個人資料和申請案件的 API 端點
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import JSONResponse, Response
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import json
import base64
from app.models import User
from app.middleware.auth import get_current_user
from app.services.individual_service import IndividualService
from app.services.application_service import ApplicationService

# 創建路由器
router = APIRouter(prefix="/api/v2")

# === Pydantic 模型定義 ===

class IndividualRequest(BaseModel):
    chinese_last_name: str
    chinese_first_name: str
    english_last_name: str
    english_first_name: str
    id_card_front_image: Optional[str] = None  # Base64 編碼的圖片
    id_card_back_image: Optional[str] = None   # Base64 編碼的圖片

class ApplicationRequest(BaseModel):
    application_type: str  # '首來族', '換證', '遺失件'
    urgency: str          # '急件', '普通件'
    application_date: Optional[str] = None
    customer_name: str
    status: Optional[str] = '草稿'
    substatus: Optional[str] = None
    reason: Optional[str] = None
    individual_data: IndividualRequest

class ApplicationUpdateRequest(BaseModel):
    application_type: Optional[str] = None
    urgency: Optional[str] = None
    application_date: Optional[str] = None
    customer_name: Optional[str] = None
    status: Optional[str] = None
    substatus: Optional[str] = None
    reason: Optional[str] = None
    individual_data: Optional[IndividualRequest] = None

# === 個人資料相關 API ===

@router.post('/individuals')
def create_individual(individual: IndividualRequest, current_user: User = Depends(get_current_user)):
    """創建個人資料"""
    try:
        result = IndividualService.create_individual(individual.dict())
        
        if result['success']:
            return JSONResponse({
                'success': True,
                'individual_id': result['individual_id'],
                'message': result['message']
            }, status_code=201)
        else:
            return JSONResponse({
                'success': False,
                'error': result['error']
            }, status_code=400)
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'伺服器錯誤: {str(e)}')

@router.get('/individuals/{individual_id}')
def get_individual(individual_id: int, current_user: User = Depends(get_current_user)):
    """獲取個人資料詳情"""
    try:
        individual = IndividualService.get_individual_by_id(individual_id)
        
        if individual:
            return JSONResponse({
                'success': True,
                'data': individual
            })
        else:
            return JSONResponse({
                'success': False,
                'error': '找不到該個人資料'
            }, status_code=404)
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'伺服器錯誤: {str(e)}')

@router.put('/individuals/{individual_id}')
def update_individual(individual_id: int, update_data: IndividualRequest, current_user: User = Depends(get_current_user)):
    """更新個人資料"""
    try:
        result = IndividualService.update_individual(individual_id, update_data.dict(exclude_unset=True))
        
        if result['success']:
            return JSONResponse({
                'success': True,
                'message': result['message']
            })
        else:
            return JSONResponse({
                'success': False,
                'error': result['error']
            }, status_code=400)
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'伺服器錯誤: {str(e)}')

@router.get('/individuals/{individual_id}/images/{image_type}')
def get_individual_image(individual_id: int, image_type: str, current_user: User = Depends(get_current_user)):
    """獲取個人資料的圖片"""
    try:
        if image_type not in ['front', 'back']:
            return JSONResponse({
                'success': False,
                'error': '圖片類型必須是 front 或 back'
            }, status_code=400)
        
        image_data = IndividualService.get_individual_image(individual_id, image_type)
        
        if image_data:
            return Response(
                content=image_data,
                media_type='image/jpeg',
                headers={'Content-Disposition': f'inline; filename="id_card_{image_type}.jpg"'}
            )
        else:
            return JSONResponse({
                'success': False,
                'error': '找不到該圖片'
            }, status_code=404)
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'伺服器錯誤: {str(e)}')

# === 申請案件相關 API ===

@router.post('/applications')
def create_application(application: ApplicationRequest, current_user: User = Depends(get_current_user)):
    """創建申請案件（包含個人資料的新增/更新）"""
    try:
        result = ApplicationService.create_application(application.dict(), current_user.id)
        
        if result['success']:
            return JSONResponse({
                'success': True,
                'application_id': result['application_id'],
                'individual_id': result['individual_id'],
                'individual_action': result['individual_action'],
                'message': result['message']
            }, status_code=201)
        else:
            return JSONResponse({
                'success': False,
                'error': result['error']
            }, status_code=400)
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'伺服器錯誤: {str(e)}')

@router.get('/applications')
def get_user_applications(status: Optional[str] = None, current_user: User = Depends(get_current_user)):
    """獲取當前用戶的申請案件列表"""
    try:
        applications = ApplicationService.get_applications_by_user(current_user.id, status)
        
        return JSONResponse({
            'success': True,
            'data': applications
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'伺服器錯誤: {str(e)}')

@router.get('/applications/{application_id}')
def get_application(application_id: int, current_user: User = Depends(get_current_user)):
    """獲取申請案件詳情"""
    try:
        # 檢查是否為管理員
        user_id = None if current_user.is_admin else current_user.id
        
        application = ApplicationService.get_application_by_id(application_id, user_id)
        
        if application:
            return JSONResponse({
                'success': True,
                'data': application
            })
        else:
            return JSONResponse({
                'success': False,
                'error': '找不到該申請案件或無權限查看'
            }, status_code=404)
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'伺服器錯誤: {str(e)}')

@router.put('/applications/{application_id}')
def update_application(application_id: int, update_data: ApplicationUpdateRequest, current_user: User = Depends(get_current_user)):
    """更新申請案件"""
    try:
        # 檢查是否為管理員
        user_id = None if current_user.is_admin else current_user.id
        
        result = ApplicationService.update_application(
            application_id, 
            update_data.dict(exclude_unset=True), 
            user_id
        )
        
        if result['success']:
            return JSONResponse({
                'success': True,
                'message': result['message']
            })
        else:
            return JSONResponse({
                'success': False,
                'error': result['error']
            }, status_code=400)
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'伺服器錯誤: {str(e)}')

@router.delete('/applications/{application_id}')
def delete_application(application_id: int, current_user: User = Depends(get_current_user)):
    """刪除申請案件"""
    try:
        # 檢查是否為管理員
        user_id = None if current_user.is_admin else current_user.id
        
        result = ApplicationService.delete_application(application_id, user_id)
        
        if result['success']:
            return JSONResponse({
                'success': True,
                'message': result['message']
            })
        else:
            return JSONResponse({
                'success': False,
                'error': result['error']
            }, status_code=400)
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'伺服器錯誤: {str(e)}')

# === 管理員專用 API ===

@router.get('/admin/applications')
def get_all_applications(
    status: Optional[str] = None, 
    page: int = 1, 
    limit: int = 50, 
    current_user: User = Depends(get_current_user)
):
    """獲取所有申請案件（管理員專用）"""
    try:
        if not current_user.is_admin:
            return JSONResponse({
                'success': False,
                'error': '權限不足，僅管理員可使用'
            }, status_code=403)
        
        result = ApplicationService.get_all_applications(status, page, limit)
        
        if result['success']:
            return JSONResponse({
                'success': True,
                'data': result['data'],
                'pagination': result['pagination']
            })
        else:
            return JSONResponse({
                'success': False,
                'error': result['error']
            }, status_code=400)
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'伺服器錯誤: {str(e)}')

@router.put('/admin/applications/{application_id}/status')
def update_application_status(
    application_id: int, 
    status_data: dict,
    current_user: User = Depends(get_current_user)
):
    """更新申請案件狀態（管理員專用）"""
    try:
        if not current_user.is_admin:
            return JSONResponse({
                'success': False,
                'error': '權限不足，僅管理員可使用'
            }, status_code=403)
        
        # 管理員可以更新任何申請的狀態
        result = ApplicationService.update_application(application_id, status_data, None)
        
        if result['success']:
            return JSONResponse({
                'success': True,
                'message': result['message']
            })
        else:
            return JSONResponse({
                'success': False,
                'error': result['error']
            }, status_code=400)
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'伺服器錯誤: {str(e)}')

# === 通用 API ===

@router.post('/upload-image')
def upload_image(file: UploadFile = File(...), current_user: User = Depends(get_current_user)):
    """上傳圖片並返回 Base64 編碼"""
    try:
        if not file.content_type.startswith('image/'):
            return JSONResponse({
                'success': False,
                'error': '請上傳圖片文件'
            }, status_code=400)
        
        # 讀取文件內容
        image_data = file.file.read()
        
        # 轉換為 Base64
        base64_data = base64.b64encode(image_data).decode('utf-8')
        
        return JSONResponse({
            'success': True,
            'data': {
                'filename': file.filename,
                'content_type': file.content_type,
                'size': len(image_data),
                'base64_data': f"data:{file.content_type};base64,{base64_data}"
            }
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'圖片上傳失敗: {str(e)}')