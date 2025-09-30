from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.auth_service import AuthService
from typing import Optional

router = APIRouter(prefix="/auth")


# Pydantic models for request validation
class LoginRequest(BaseModel):
    username: str
    password: str


class RegisterRequest(BaseModel):
    username: str
    password: str
    company: Optional[str] = ''
    email: Optional[str] = ''


class ChangePasswordRequest(BaseModel):
    username: str
    old_password: str
    new_password: str


class TokenRequest(BaseModel):
    token: str


@router.post('/login')
def login(request: LoginRequest):
    """用戶登入端點"""
    auth_service = AuthService()
    try:
        result = auth_service.login(request.username, request.password)
        if result:
            return {'message': 'Login successful', 'user': result}
        raise HTTPException(status_code=401, detail='Invalid username or password')
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'Login failed: {str(e)}')


@router.post('/register')
def register(request: RegisterRequest):
    """用戶註冊端點"""
    auth_service = AuthService()
    try:
        result = auth_service.register(request.username, request.password, request.company, request.email)
        if result:
            return {'message': 'User registered successfully', 'user': result}
        raise HTTPException(status_code=400, detail='Registration failed - user may already exist')
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'Registration failed: {str(e)}')


@router.post('/change-password')
def change_password(request: ChangePasswordRequest):
    """修改密碼端點"""
    auth_service = AuthService()
    try:
        success = auth_service.change_password(
            request.username, 
            request.old_password, 
            request.new_password
        )
        if success:
            return {'message': 'Password changed successfully'}
        raise HTTPException(status_code=400, detail='Password change failed - invalid credentials')
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'Password change failed: {str(e)}')


@router.post('/validate-token')
def validate_token(request: TokenRequest):
    """驗證token端點"""
    auth_service = AuthService()
    try:
        payload = auth_service.validate_token(request.token)
        if payload:
            return {'valid': True, 'payload': payload}
        raise HTTPException(status_code=401, detail='Invalid or expired token')
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'Token validation failed: {str(e)}')


@router.post('/refresh-token')
def refresh_token(request: TokenRequest):
    """刷新token端點"""
    auth_service = AuthService()
    try:
        new_token = auth_service.refresh_token(request.token)
        if new_token:
            return {'message': 'Token refreshed successfully', 'token': new_token}
        raise HTTPException(status_code=401, detail='Token refresh failed')
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'Token refresh failed: {str(e)}')


@router.post('/logout')
def logout(request: TokenRequest):
    """用戶登出端點"""
    auth_service = AuthService()
    try:
        success = auth_service.logout(request.token)
        if success:
            return {'message': 'Logout successful'}
        raise HTTPException(status_code=400, detail='Logout failed')
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'Logout failed: {str(e)}')