import google.generativeai as genai
import json
import os
import random
from dotenv import load_dotenv

# 기존 환경 설정 유지
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def generate_random_quiz(user_daily_count=0, lang="ko"):
    try:
        # ✅ 요청하신 품목 리스트 그대로 반영
        recycling_topics = [
            "영수증", "우산", "건전지", "형광등", "음식물이 묻은 배달용기",
            "컵라면 용기", "아이스팩", "깨진 유리", "사기그릇", "알약 포장재",
            "화장품 병", "스프링 노트", "뽁뽁이(에어캡)", "은박지/호일", "나무젓가락",
            "헌 옷", "신발", "CD/DVD", "장난감", "보온보냉팩", "과일 껍질", "동물 뼈"
        ]
        
        # ✅ 무작위 3개 추출 로직 유지
        selected_topics = random.sample(recycling_topics, 3)

        # ✅ 수정 요청하신 System / User 분리 구조 적용 (2.5 flash)
        SYSTEM_PROMPT = """You are RecyQ's quiz AI. Output ONLY a valid JSON array. No extra text."""

        USER_PROMPT = f"""
언어: {lang}
아래 3개 품목에 대한 OX 퀴즈를 JSON 배열로 출력하라.
품목: {selected_topics[0]}, {selected_topics[1]}, {selected_topics[2]}

[형식 가이드]
[
  {{
    "question": "질문",
    "answer": "O/X",
    "explanation": "해설"
  }}
]"""

        model = genai.GenerativeModel(
            model_name='gemini-2.5-flash',
            system_instruction=SYSTEM_PROMPT
        )

        # 퀴즈 생성 실행
        response = model.generate_content(
            USER_PROMPT,
            generation_config={
                "response_mime_type": "application/json",
                "temperature": 0.8
            }
        )
        
        return json.loads(response.text)
        
    except Exception as e:
        print(f"🚨 퀴즈 생성 에러: {e}")
        return []