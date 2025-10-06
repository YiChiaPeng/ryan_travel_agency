"""
LLM服務 - 使用OpenAI GPT模型進行文字解析
"""
import json
import logging
import os
from typing import Optional, Dict, Any
import openai
from openai import OpenAI

logger = logging.getLogger(__name__)

class LLMService:
    def __init__(self):
        # 從環境變數獲取API金鑰
        self.api_key = os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            logger.warning("OPENAI_API_KEY 環境變數未設定，LLM功能將不可用")
            self.client = None
        else:
            try:
                self.client = OpenAI(api_key=self.api_key)
            except Exception as e:
                logger.warning(f"OpenAI客戶端初始化失敗: {e}")
                self.client = None
    
    def extract_passport_info(self, ocr_text: str) -> Optional[Dict[str, Any]]:
        """
        使用LLM從OCR文字中提取護照資訊
        
        Args:
            ocr_text: OCR識別的文字內容
            
        Returns:
            提取的護照資訊字典，如果失敗則返回None
        """
        if not self.client:
            raise Exception("OpenAI API 未配置，請設定 OPENAI_API_KEY 環境變數")
        
        try:
            prompt = self._create_passport_extraction_prompt(ocr_text)
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",  # 或使用 "gpt-4" 以獲得更好的準確度
                messages=[
                    {
                        "role": "system",
                        "content": "你是一個專業的護照資訊提取助手。請仔細分析OCR識別的護照文字，準確提取個人資訊，並以指定的JSON格式返回。"
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.1,  # 降低隨機性以提高準確度
                max_tokens=500
            )
            
            result_text = response.choices[0].message.content.strip()
            logger.info(f"LLM 原始回應: {result_text}")
            
            # 嘗試解析JSON
            parsed_info = self._parse_llm_response(result_text)
            
            if parsed_info:
                logger.info(f"護照資訊提取成功: {json.dumps(parsed_info, ensure_ascii=False)}")
                return parsed_info
            else:
                logger.warning("LLM返回的不是有效的JSON格式")
                return None
                
        except Exception as e:
            logger.error(f"LLM處理失敗: {str(e)}")
            raise Exception(f"LLM處理失敗: {str(e)}")
    
    def _create_passport_extraction_prompt(self, ocr_text: str) -> str:
        """
        創建護照資訊提取的提示詞
        """
        return f"""
請從以下OCR識別的護照文字中提取個人資訊，並以JSON格式返回：

OCR文字內容：
{ocr_text}

請提取以下資訊並返回JSON格式（如果某項資訊無法識別則設為null）：
{{
  "chineseLastName": "中文姓",
  "chineseFirstName": "中文名", 
  "englishLastName": "英文姓",
  "englishFirstName": "英文名",
  "birthDate": "出生日期(YYYY-MM-DD格式)",
  "gender": "性別(男/女)",
  "nationalId": "身分證字號或護照號碼"
}}

提取規則：
1. 中文姓名：通常在護照的中文區域或姓名欄位
2. 英文姓名：在 "Name/Surname" 或 "Given Names" 欄位
3. 出生日期：在 "Date of birth" 欄位，請轉換為 YYYY-MM-DD 格式
4. 性別：在 "Sex" 欄位（M=男，F=女）
5. 護照號碼：在 "Passport No." 或類似欄位
6. 如果是中華民國護照，可能包含身分證字號

請只返回JSON格式的結果，不要包含其他說明文字。
"""
    
    def _parse_llm_response(self, response_text: str) -> Optional[Dict[str, Any]]:
        """
        解析LLM的回應文字，提取JSON內容
        """
        try:
            # 直接嘗試解析JSON
            return json.loads(response_text)
        except json.JSONDecodeError:
            # 如果直接解析失敗，嘗試找到JSON部分
            try:
                # 查找JSON開始和結束位置
                start = response_text.find('{')
                end = response_text.rfind('}') + 1
                
                if start >= 0 and end > start:
                    json_text = response_text[start:end]
                    return json.loads(json_text)
                    
            except json.JSONDecodeError:
                pass
            
            logger.error(f"無法解析LLM回應為JSON: {response_text}")
            return None
    
    def test_llm_setup(self) -> dict:
        """
        測試LLM設定是否正常
        """
        if not self.client:
            return {
                "status": "error",
                "error": "OPENAI_API_KEY 未設定",
                "message": "請設定 OPENAI_API_KEY 環境變數"
            }
        
        try:
            # 發送簡單的測試請求
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "user",
                        "content": "請回覆 'API測試成功'"
                    }
                ],
                max_tokens=10
            )
            
            result = response.choices[0].message.content.strip()
            
            return {
                "status": "success",
                "test_response": result,
                "model": "gpt-3.5-turbo"
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "message": "OpenAI API 連接失敗"
            }

# 創建全局實例
llm_service = LLMService()