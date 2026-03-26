import os
import google.generativeai as genai
from dotenv import load_dotenv

def setup_gemini():
    # 1. 금고(.env 파일) 문을 엽니다.
    load_dotenv()
    
    # 2. 금고에서 'GEMINI_API_KEY'라는 이름표가 붙은 실제 키를 꺼내옵니다.
    api_key = os.getenv("GEMINI_API_KEY")
    
    if not api_key:
        raise ValueError("❌ 환경 변수에 API 키가 없습니다! .env 파일을 확인해 주세요.")
        
    # 3. 안전하게 꺼내온 키로 AI를 세팅합니다.
    genai.configure(api_key=api_key)
