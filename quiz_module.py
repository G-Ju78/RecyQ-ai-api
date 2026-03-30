import google.generativeai as genai
import json
import random # 🌟 매번 다른 퀴즈를 위해 무작위 주제 추출 라이브러리 활용

# 자바(Spring Boot)가 요구하는 규격에 맞춰 3문제를 한 번에 생성합니다.
def generate_random_quiz(user_daily_count=0, lang="ko"):
    try:
        # 사용자가 지정한 기존 모델 설정 유지
        model = genai.GenerativeModel('gemini-2.5-flash')

        # 🌟 1. AI가 특정 문제만 반복하지 않도록 다양한 재활용 품목 리스트를 준비합니다.
        recycling_topics = [
            "영수증", "우산", "건전지", "형광등", "음식물이 묻은 배달용기",
            "컵라면 용기", "아이스팩", "깨진 유리", "사기그릇", "알약 포장재",
            "화장품 병", "스프링 노트", "뽁뽁이(에어캡)", "은박지/호일", "나무젓가락",
            "헌 옷", "신발", "CD/DVD", "장난감", "보온보냉팩", "과일 껍질", "동물 뼈"
        ]

        # 🌟 2. 위 후보군에서 무작위로 3개를 추출하여 AI에게 출제를 명령합니다.
        selected_topics = random.sample(recycling_topics, 3)
        
        # 🌟 3. 추출된 주제를 기반으로 한 프롬프트 구성
        prompt = f"""
        당신은 친환경 분리배출 플랫폼 'RecyQ'의 퀴즈 출제 AI입니다.
        언어: {lang}

        [출제 규칙]
        - 반드시 다음 3가지 품목에 대한 OX 퀴즈를 순서대로 하나씩 출제하세요: 
          1번 문제: {selected_topics[0]}
          2번 문제: {selected_topics[1]}
          3번 문제: {selected_topics[2]}
        - 실생활에서 자주 헷갈리는 분리배출 상식 3문제를 출제하세요.
        - 정답이 명확하게 O 또는 X인 문제만 만드세요. (애매한 문제 금지)
        - 해설은 왜 그런지 이유를 포함해 2~3문장으로 작성하세요.

        [응답 형식 - 🌟 오직 아래 형태의 JSON 배열(Array)로만 출력하세요, 다른 텍스트 금지!]
        [
            {{
                "question": "질문 내용",
                "answer": "O 또는 X",
                "explanation": "상세 해설"
            }}
        ]
        """
        
        # 🌟 4. JSON 응답 강제 및 Temperature 설정 (0.8로 설정하여 다양성 극대화)
        response = model.generate_content(
            prompt,
            generation_config={
                "response_mime_type": "application/json",
                "temperature": 0.8
            }
        )
        
        # AI가 생성한 JSON 텍스트를 파이썬 리스트로 변환
        quiz_list = json.loads(response.text)
        
        # 자바 서버로 최종 3문제 배열 반환
        return quiz_list
        
    except Exception as e:
        print("🚨 퀴즈 생성 에러:", e)
        # 에러 발생 시 시스템 중단을 막기 위해 빈 배열 반환
        return []

# 💡 참고: 포인트 지급 로직(calculate_quiz_reward)은 
# 이제 자바(QuizController)가 담당하므로 이 모듈에서는 삭제되었습니다.