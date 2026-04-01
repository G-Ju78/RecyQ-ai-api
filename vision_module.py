import google.generativeai as genai
import PIL.Image
import json
import os
from dotenv import load_dotenv

# 1. .env 파일에 있는 환경 변수들을 파이썬으로 불러옵니다.
load_dotenv()

# 2. .env 파일에 작성된 API 키의 '이름'을 가져옵니다. 
# (주의: "GOOGLE_API_KEY" 부분은 PM님의 .env 파일에 적힌 실제 변수명과 똑같아야 합니다!)
api_key = os.getenv("GEMINI_API_KEY")

# 3. 안전하게 불러온 키를 세팅합니다. (하드코딩 X)
genai.configure(api_key=api_key)

def analyze_trash(image_path, lang="ko", user_id="회원"):
    try:
        model = genai.GenerativeModel('gemini-2.5-flash')
        # 핵심 수정: .convert('RGB')를 붙여서 MPO 등 특수 포맷을 일반 이미지로 강제 변환!
        img = PIL.Image.open(image_path).convert('RGB')
        
        prompt = f"""
        당신은 친환경 분리배출 플랫폼 'RecyQ'의 '자원순환 수석 컨설턴트 AI'입니다.
        실제 지자체 공무원이 아님을 명심하고, AI 조력자로서 시민이 촬영한 쓰레기 사진을 분석해 리포트를 생성하세요.

        [중요: 보상 적격 여부(is_reward_eligible) 판단 기준 - 매우 관대하게!]
        - 우리의 목적은 '완벽한 분리배출'이 아니라 '시민들의 참여 독려'입니다.
        - 사진 속에 '재활용이 가능한 품목(플라스틱, 종이, 캔 등)'이 찍혀있다면 무조건 true를 부여하세요.
        - 라벨이 안 떼어져 있거나, 테이프가 붙어있거나, 국물 자국이 남아있어도 참여 자체를 칭찬하며 true를 줍니다. (대신 guide 항목에서 "다음엔 이렇게 해주시면 더 좋아요"라고 부드럽게 안내하세요.)
        - 오직 '원래 일반쓰레기인 것(사용한 휴지 등)'이거나 '쓰레기가 아닌 것(사람 얼굴, 풍경)'일 때만 false를 부여하세요.

        [🌟 중요: 개인화 메시지]
        - 상태 요약(status_message)이나 격려 메시지(point_reason)를 작성할 때 '시민' 대신 반드시 '{user_id}님'이라고 사용자의 이름을 다정하게 불러주세요. 
        - 예: "훌륭해요! {user_id}님 덕분에 버려질 뻔한 자원을 구했습니다!"
        
        언어: {lang}

        [응답 형식 - 반드시 아래 JSON 키를 100% 똑같이 유지할 것]
        {{
            "detected_item": "품목명 (예: 투명 페트병)",
            "item_count": 사진 속에 있는 재활용품의 개수 (정수로 출력, 예: 3),
            "is_dirty": 오염 여부(boolean: true 또는 false),
            "status_message": "상태 요약 (AI 컨설턴트로서 친절하게)",
            "guide": "1. ...\\n2. ...\\n3. ... (반드시 번호 매기기와 줄바꿈 \\n 을 사용할 것)",
            "point_reason": "격려 메시지 및 피드백 (실수가 있어도 칭찬,반드시 {user_id}님을 부를 것)",
            "is_reward_eligible": 보상 적격(boolean: true 또는 false)
        }}
        """
        response = model.generate_content(
            [prompt, img],
            # 완벽한 JSON 포맷 강제 출력
            generation_config={"response_mime_type": "application/json"}
        )
        return json.loads(response.text)
        
    except Exception as e:
        print(f"🚨 비전 AI 에러 발생: {e}")
        # 핵심 수정: 에러가 나더라도 자바가 null을 띄우지 않도록 기본 형식의 JSON을 반환합니다.
        return {
            "detected_item": "분석 지연 (재촬영 요망)",
            "item_count": 1,
            "is_dirty": False,
            "status_message": "현재 AI 컨설턴트가 너무 많은 분석을 처리하고 있어요.",
            "guide": "잠시 후 다시 촬영해주시거나, 밝은 곳에서 쓰레기 전체가 잘 보이게 찍어주세요!",
            "point_reason": "네트워크 지연으로 분석을 완료하지 못했습니다.",
            "is_reward_eligible": False
        }