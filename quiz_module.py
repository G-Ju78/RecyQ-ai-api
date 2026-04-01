import google.generativeai as genai
import json
import random # 🌟 무작위 추출을 위해 파이썬 기본 랜덤 라이브러리 추가!

# 자바(Spring Boot)가 요구하는 규격에 맞춰 3문제를 한 번에 생성합니다.
def generate_random_quiz(user_daily_count=0, lang="ko"):
    try:
        model = genai.GenerativeModel('gemini-2.5-flash')

        # 🌟 1. AI가 매번 뻔한 것만 고르지 못하도록, 다양한 재활용 품목 후보군을 준비합니다.
        recycling_topics = [
            "영수증", "우산", "건전지", "형광등", "음식물이 묻은 배달용기",
            "컵라면 용기", "아이스팩", "깨진 유리", "사기그릇", "알약 포장재",
            "화장품 병", "스프링 노트", "뽁뽁이(에어캡)", "은박지/호일", "나무젓가락",
            "헌 옷", "신발", "CD/DVD", "장난감", "보온보냉팩", "과일 껍질", "동물 뼈"
        ]

        # 🌟 2. 위 후보군 리스트에서 무작위로 딱 3개만 뽑아냅니다. (매번 달라짐!)
        selected_topics = random.sample(recycling_topics, 3)
        
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
        - 3문제가 서로 다른 품목이 되도록 구성하세요. (예: 영수증, 우산, 전자기기 등)
        - 해설은 왜 그런지 이유를 포함해 2~3문장으로 작성하세요.

        [응답 형식 - 🌟 오직 아래 형태의 JSON 배열(Array)로만 출력하세요, 다른 텍스트 금지!]
        [
            {{
                "question": "페트병을 버릴 때는 라벨을 떼지 않아도 된다?",
                "answer": "X",
                "explanation": "페트병의 비닐 라벨은 재질이 달라 재활용을 방해하므로 반드시 떼어주세요."
            }},
            {{
                "question": "기름이 묻은 피자 박스는 종이류로 버린다?",
                "answer": "X",
                "explanation": "음식물로 심하게 오염된 종이는 재활용이 불가능하므로 일반 쓰레기로 버려야 합니다."
            }},
            {{
                "question": "깨진 유리는 신문지에 싸서 종량제 봉투에 버린다?",
                "answer": "O",
                "explanation": "수거 작업자가 다치지 않도록 두껍게 싸서 버리거나 특수 마대에 버려야 합니다."
            }}
        ]
        """
        
        # 🌟 4. generation_config에 temperature 값을 추가하여 창의성을 높입니다! (0.0 ~ 2.0 사이, 높을수록 랜덤)
        response = model.generate_content(
            prompt,
            generation_config={
                "response_mime_type": "application/json",
                "temperature": 0.8  # 기본값보다 높여서 답변을 훨씬 다채롭게 만듦
            }
        )
        
        # AI가 만들어준 JSON 텍스트를 파이썬 리스트로 변환
        quiz_list = json.loads(response.text)
        
        # 자바에게 3문제 배열을 그대로 던져줍니다!
        return quiz_list
        
    except Exception as e:
        print("🚨 퀴즈 생성 에러:", e)
        # 에러 시 서버가 죽지 않도록 빈 배열 반환
        return [{"error": str(e)}]

# 💡 하단의 calculate_quiz_reward 함수는 이제 자바(QuizController)가 
# 포인트 로직을 담당하므로 완전히 삭제하셔도 무방합니다.