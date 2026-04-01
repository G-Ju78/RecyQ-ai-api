import google.generativeai as genai
import PIL.Image
import json
import os
from dotenv import load_dotenv

# 1. 환경 변수 로드
load_dotenv()

# 2. API 키 설정 (보안을 위해 .env 관리 권장)
api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)

def analyze_trash(image_path, lang="ko", user_id="회원"):
    try:
        # [모델 설정] 요청하신 2.5 flash 모델 반영
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        # [이미지 전처리] MPO 등 특수 포맷 대응을 위한 RGB 변환 유지
        img = PIL.Image.open(image_path).convert('RGB')
        
        # [프롬프트] 기존 틀 + 권주님의 새로운 요구사항(표 형식/호칭) 반영
        prompt = f"""당신은 친환경 분리배출 플랫폼 'RecyQ'의 AI 자원순환 컨설턴트입니다.
사진을 분석하고 반드시 아래의 JSON 데이터만 출력하세요. 설명이나 마크다운 없이 JSON만 반환하세요.

## 출력 형식 (키 이름 변경 금지)
{{
  "detected_item": "품목명 (예: 투명 페트병)",
  "item_count": 정수,
  "is_dirty": boolean,
  "status_message": "상태 요약 — 반드시 '{user_id}님'으로 호칭",
  "guide": "1. ..\\n2. ..\\n3. ..",
  "point_reason": "격려 메시지 — 반드시 '{user_id}님'으로 호칭",
  "is_reward_eligible": boolean
}}

## 보상 적격(is_reward_eligible) 판단표 (매우 관대하게!)
| 상황 | 결과 |
|---|---|
| 재활용 가능 품목(플라스틱·종이·캔·유리 등)이 보임 | true |
| 라벨 미제거 / 테이프 부착 / 약간의 오염 | true (참여 독려) |
| 명백한 일반쓰레기 / 사람이 들어간 사진 / 풍경 | false |

언어: {lang}
"""
        
        # 모델 실행 및 JSON 응답 강제
        response = model.generate_content(
            [prompt, img],
            generation_config={"response_mime_type": "application/json"}
        )
        
        return json.loads(response.text)
        
    except Exception as e:
        # 에러 발생 시에도 Java 서버가 null을 받지 않도록 기본값 반환
        print(f"🚨 비전 AI 에러 발생: {e}")
        return {
            "detected_item": "분석 지연",
            "item_count": 0,
            "is_dirty": False,
            "status_message": f"현재 시스템이 바빠서 {user_id}님의 사진을 분석하지 못했습니다.",
            "guide": "잠시 후 다시 촬영해주시거나, 밝은 곳에서 찍어주세요!",
            "point_reason": "네트워크 연결 확인이 필요합니다.",
            "is_reward_eligible": False
        }