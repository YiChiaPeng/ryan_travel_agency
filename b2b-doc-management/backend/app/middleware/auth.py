"""
認證中間件模組
提供統一的Token驗證和用戶認證功能
"""
from fastapi import HTTPException, Header, Depends
from typing import Optional
from app.services.auth_service import AuthService
from app.models import User


def get_bearer_token(authorization: str = Header(None)) -> str:
    """
    從Authorization header中提取Bearer token
    
    Args:
        authorization: Authorization header值
        
    Returns:
        提取的token字符串
        
    Raises:
        HTTPException: 當header格式不正確時
    """
    if not authorization:
        raise HTTPException(
            status_code=401, 
            detail='Unauthorized - Missing authorization header'
        )
    
    if not authorization.startswith('Bearer '):
        raise HTTPException(
            status_code=401, 
            detail='Unauthorized - Invalid authorization header format'
        )
    
    return authorization.split(' ', 1)[1]


def get_current_user(token: str = Depends(get_bearer_token)) -> User:
    """
    根據token獲取當前用戶
    
    Args:
        token: JWT token
        
    Returns:
        當前用戶對象
        
    Raises:
        HTTPException: 當token無效或用戶不存在時
    """
    auth_service = AuthService()
    user = auth_service.get_user_by_token(token)
    
    if not user:
        raise HTTPException(
            status_code=401, 
            detail='Unauthorized - Invalid or expired token'
        )
    
    return user


def get_current_admin(current_user: User = Depends(get_current_user)) -> User:
    """
    檢查當前用戶是否為管理員
    
    Args:
        current_user: 當前用戶對象
        
    Returns:
        管理員用戶對象
        
    Raises:
        HTTPException: 當用戶不是管理員時
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=403, 
            detail='Forbidden - Admin privileges required'
        )
    
    return current_user


def get_optional_user(authorization: str = Header(None)) -> Optional[User]:
    """
    可選的用戶認證，不會拋出異常
    
    Args:
        authorization: Authorization header值
        
    Returns:
        用戶對象或None
    """
    try:
        if not authorization or not authorization.startswith('Bearer '):
            return None
        
        token = authorization.split(' ', 1)[1]
        auth_service = AuthService()
        return auth_service.get_user_by_token(token)
    except Exception:
        return None


def verify_user_permission(
    current_user: User, 
    target_user_id: int, 
    allow_admin: bool = True
) -> bool:
    """
    驗證用戶權限
    
    Args:
        current_user: 當前用戶
        target_user_id: 目標用戶ID
        allow_admin: 是否允許管理員訪問
        
    Returns:
        是否有權限
    """
    if current_user.id == target_user_id:
        return True
    
    if allow_admin and current_user.is_admin:
        return True
    
    return False


def verify_company_permission(
    current_user: User, 
    target_company: str, 
    allow_admin: bool = True
) -> bool:
    """
    驗證公司權限
    
    Args:
        current_user: 當前用戶
        target_company: 目標公司名稱
        allow_admin: 是否允許管理員訪問
        
    Returns:
        是否有權限
    """
    if current_user.company_name == target_company:
        return True
    
    if allow_admin and current_user.is_admin:
        return True
    
    return False