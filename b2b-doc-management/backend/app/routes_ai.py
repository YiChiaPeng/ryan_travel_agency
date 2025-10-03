"""
OCR和LLM相關的API路由 - FastAPI版本
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, Dict, Any
from .middleware.auth import get_current_user
from .services.ocr_service import ocr_service
from .services.llm_service import llm_service
import logging

logger = logging.getLogger(__name__)

# 創建路由器
router = APIRouter(prefix="/api", tags=["AI"])

# 請求模型
class OCRRequest(BaseModel):
    image: str  # Base64編碼的圖片
    language: Optional[str] = "chi_tra+eng"

class LLMRequest(BaseModel):
    ocrText: str
    prompt: Optional[str] = None

class CompleteExtractionRequest(BaseModel):
    image: str  # Base64編碼的圖片
    language: Optional[str] = "chi_tra+eng"

@router.post("/ocr/extract")
async def extract_text_ocr(
    request: OCRRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    OCR文字提取API
    """
    try:
        # 執行OCR
        extracted_text = ocr_service.extract_text_from_base64(
            request.image, 
            request.language
        )
        
        return {
            'success': True,
            'text': extracted_text,
            'language': request.language
        }
        
    except Exception as e:
        logger.error(f"OCR API 錯誤: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/llm/extract-passport-info")
async def extract_passport_info_llm(
    request: LLMRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    LLM護照資訊提取API
    """
    try:
        # 使用LLM提取護照資訊
        extracted_info = llm_service.extract_passport_info(request.ocrText)
        
        if extracted_info:
            return {
                'success': True,
                'result': extracted_info,
                'raw_ocr': request.ocrText
            }
        else:
            raise HTTPException(
                status_code=422, 
                detail='無法從OCR文字中提取有效的護照資訊'
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"LLM API 錯誤: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/ocr/test")
async def test_ocr(current_user: dict = Depends(get_current_user)):
    """
    測試OCR設定
    """
    try:
        result = ocr_service.test_ocr_setup()
        return result
        
    except Exception as e:
        logger.error(f"OCR測試錯誤: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/llm/test")
async def test_llm(current_user: dict = Depends(get_current_user)):
    """
    測試LLM設定
    """
    try:
        result = llm_service.test_llm_setup()
        return result
        
    except Exception as e:
        logger.error(f"LLM測試錯誤: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/extract-passport-complete")
async def extract_passport_complete(
    request: CompleteExtractionRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    完整的護照資訊提取流程：OCR + LLM
    """
    try:
        # 步驟1: OCR提取文字
        logger.info("開始OCR文字提取...")
        ocr_text = ocr_service.extract_text_from_base64(
            request.image, 
            request.language
        )
        
        if not ocr_text.strip():
            raise HTTPException(
                status_code=422,
                detail={
                    'error': 'OCR未能識別到任何文字',
                    'ocr_text': ocr_text
                }
            )
        
        # 步驟2: LLM解析護照資訊
        logger.info("開始LLM護照資訊解析...")
        extracted_info = llm_service.extract_passport_info(ocr_text)
        
        if extracted_info:
            return {
                'success': True,
                'extracted_info': extracted_info,
                'ocr_text': ocr_text,
                'processing_steps': [
                    'OCR文字提取完成',
                    'LLM護照資訊解析完成'
                ]
            }
        else:
            raise HTTPException(
                status_code=422,
                detail={
                    'error': '無法從OCR文字中提取有效的護照資訊',
                    'ocr_text': ocr_text,
                    'processing_steps': [
                        'OCR文字提取完成',
                        'LLM護照資訊解析失敗'
                    ]
                }
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"完整護照提取流程錯誤: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))