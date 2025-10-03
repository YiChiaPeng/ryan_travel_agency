"""
OCR服務 - 使用Tesseract進行圖片文字識別
"""
import base64
import io
import tempfile
import os
from PIL import Image
import pytesseract
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class OCRService:
    def __init__(self):
        # 配置Tesseract路徑（如果需要）
        # pytesseract.pytesseract.tesseract_cmd = r'/usr/bin/tesseract'
        pass
    
    def extract_text_from_base64(self, image_base64: str, language: str = 'chi_tra+eng') -> str:
        """
        從Base64編碼的圖片中提取文字
        
        Args:
            image_base64: Base64編碼的圖片
            language: OCR語言設定，預設為繁體中文+英文
            
        Returns:
            提取的文字內容
        """
        try:
            # 解碼Base64圖片
            image_data = base64.b64decode(image_base64)
            image = Image.open(io.BytesIO(image_data))
            
            # 預處理圖片以提高OCR準確度
            processed_image = self._preprocess_image(image)
            
            # 執行OCR
            config = f'--oem 3 --psm 6 -l {language}'
            text = pytesseract.image_to_string(processed_image, config=config)
            
            # 清理和格式化文字
            cleaned_text = self._clean_text(text)
            
            logger.info(f"OCR提取成功，文字長度: {len(cleaned_text)}")
            return cleaned_text
            
        except Exception as e:
            logger.error(f"OCR處理失敗: {str(e)}")
            raise Exception(f"OCR處理失敗: {str(e)}")
    
    def _preprocess_image(self, image: Image.Image) -> Image.Image:
        """
        預處理圖片以提高OCR準確度
        
        Args:
            image: 原始圖片
            
        Returns:
            處理後的圖片
        """
        try:
            # 轉換為RGB模式
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # 調整圖片大小（如果太小則放大）
            width, height = image.size
            if width < 1000 or height < 1000:
                # 放大到至少1000像素
                scale_factor = max(1000 / width, 1000 / height)
                new_width = int(width * scale_factor)
                new_height = int(height * scale_factor)
                image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # 提高對比度和銳化
            from PIL import ImageEnhance
            
            # 增強對比度
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(1.5)
            
            # 增強銳度
            enhancer = ImageEnhance.Sharpness(image)
            image = enhancer.enhance(2.0)
            
            return image
            
        except Exception as e:
            logger.warning(f"圖片預處理失敗，使用原圖: {str(e)}")
            return image
    
    def _clean_text(self, text: str) -> str:
        """
        清理OCR識別的文字
        
        Args:
            text: 原始OCR文字
            
        Returns:
            清理後的文字
        """
        if not text:
            return ""
        
        # 移除多餘的空白和換行
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        
        # 合併短行（可能是OCR分割錯誤）
        cleaned_lines = []
        current_line = ""
        
        for line in lines:
            # 如果行很短且不包含關鍵詞，可能是分割錯誤
            if len(line) < 3 and current_line:
                current_line += " " + line
            else:
                if current_line:
                    cleaned_lines.append(current_line)
                current_line = line
        
        if current_line:
            cleaned_lines.append(current_line)
        
        return '\n'.join(cleaned_lines)
    
    def test_ocr_setup(self) -> dict:
        """
        測試OCR設定是否正常
        
        Returns:
            測試結果
        """
        try:
            # 創建一個簡單的測試圖片
            test_image = Image.new('RGB', (200, 50), color='white')
            
            # 嘗試執行OCR
            test_text = pytesseract.image_to_string(test_image)
            
            # 獲取Tesseract版本
            version = pytesseract.get_tesseract_version()
            
            # 獲取支援的語言
            languages = pytesseract.get_languages()
            
            return {
                "status": "success",
                "tesseract_version": str(version),
                "supported_languages": languages,
                "chinese_traditional_supported": "chi_tra" in languages,
                "english_supported": "eng" in languages
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "message": "Tesseract OCR未正確安裝或配置"
            }

# 創建全局實例
ocr_service = OCRService()