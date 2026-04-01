import google.generativeai as genai
import os
from dotenv import load_dotenv

# 1. .env 파일의 환경 변수 로드
load_dotenv()

# 2. API 키 설정 (보안을 위해 환경 변수에서 가져옴)
api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)

def get_chat_response(user_message, lang="ko"):
    """
    사용자의 질문을 받아 RecyQ AI 컨설턴트로서 답변을 생성합니다.
    시스템 지침(system_instruction)을 사용하여 인사말을 생략하고 구조를 강제합니다.
    """
    try:
        # ✅ [수정 반영] 시스템 역할 및 규칙 정의 (인사 생략, 모바일 최적화)
        system_instruction = """당신은 분리배출 플랫폼 'RecyQ'의 AI 컨설턴트입니다.

## 답변 규칙
- 🌟 인사말이나 자기소개(예: 안녕하세요 등) 절대 금지! 답변부터 즉시 시작하세요.
- 분리배출과 무관한 질문(정치, 의료 등)은 정중히 거절하세요.
- 친근하고 부드러운 대화체 사용 (~해요, ~주세요).
- 내용에 맞는 이모지를 1~2개 자연스럽게 포함 (♻️, 💧, 📦, 🌱 등).
- 전체 답변은 반드시 2~3문장 이내로 아주 간결하게 작성하세요.

## 출력 구조 (모바일 최적화)
1. 첫 번째 문장: 핵심 답변 (무엇을 어떻게 버려야 하는지 명확히 제시)
2. 엔터 두 번 (\\n\\n)
3. 두 번째 문장: 추가 설명 또는 지자체 규정 안내 (필요 시에만 작성)

## 스타일 예시
페트병은 내용물을 비우고 라벨을 제거한 뒤 찌그러뜨려 배출해 주세요! 💧

지자체마다 뚜껑 처리 방법이 다를 수 있으니 동네 규정을 확인해 보세요. ♻️"""

        # ✅ [수정 반영] Gemini 2.5 Flash 모델 설정
        model = genai.GenerativeModel(
            model_name='gemini-2.5-flash',
            system_instruction=system_instruction
        )

        # 사용자 메시지 전달 및 답변 생성
        response = model.generate_content(user_message)
        
        # 앞뒤 공백을 제거하여 깔끔한 텍스트 반환
        return {"reply": response.text.strip()}

    except Exception as e:
        print(f"🚨 채팅 모듈 에러: {e}")
        return {"reply": "잠시 연결이 원활하지 않아요. ♻️", "error": str(e)}