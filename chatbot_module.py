import google.generativeai as genai
import os
from dotenv import load_dotenv

# 1. 기존 환경 설정 및 API 키 로드 유지
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)

def get_chat_response(user_message, lang="ko"):
    try:
        # ✅ 요청하신 프롬프트 내용 그대로 적용
        system_prompt = """당신은 분리배출 플랫폼 'RecyQ'의 AI 컨설턴트입니다.

## 답변 규칙
- 인사·자기소개 없이 답변부터 시작
- 분리배출 무관 질문(정치·의료 등)은 정중히 거절
- 친근한 대화체 사용 (예: ~해요, ~주세요)
- 이모지 1~2개 자연스럽게 포함 (♻️ 💧 📦 🌱 등)

## 출력 구조 (모바일 최적화)
핵심 답변 1문장

추가 설명 1문장 (필요시에만, 지자체 차이 포함)

## 스타일 예시
페트병은 내용물을 비우고 라벨을 제거한 뒤 찌그러뜨려 배출해 주세요! 💧

지자체마다 뚜껑 처리 방법이 다를 수 있으니 동네 규정을 확인해 보세요. ♻️"""

        # ✅ 시스템과 유저 메시지 분리 구조 적용 (Gemini 2.5 Flash)
        model = genai.GenerativeModel(
            model_name='gemini-2.5-flash',
            system_instruction=system_prompt
        )

        # 챗봇 답변 생성
        response = model.generate_content(user_message)
        
        return {"reply": response.text.strip()}

    except Exception as e:
        # 에러 발생 시 처리
        print(f"🚨 에러 발생: {e}")
        return {"reply": "오류가 발생했습니다.", "error": str(e)}