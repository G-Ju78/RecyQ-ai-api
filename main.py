# main.py

from fastapi import FastAPI, File, UploadFile, Form
from pydantic import BaseModel # 🌟 챗봇 데이터를 받기 위해 새로 추가된 라이브러리
from vision_module import analyze_trash
from quiz_module import generate_random_quiz
from database import is_within_range
import chatbot_module # 🌟 PM님이 작성하신 챗봇 모듈 import!
import uvicorn
import json

app = FastAPI()

# ==========================================================================
# [1] 챗봇 데이터를 받기 위한 바구니(Model) 정의 (🌟 새로 추가됨)
# 자바(Spring Boot) 서버에서 {"question": "사용자 질문"} 형태로 데이터를 보내면
# 이 바구니가 안전하게 받아서 파이썬이 쓸 수 있게 해줍니다.
# ==========================================================================
class ChatRequest(BaseModel):
    question: str

# ==========================================================================
# [API 1] AI 환경 컨설턴트 챗봇 엔드포인트 (🌟 새로 추가됨)
# 자바의 ChatbotController가 이 주소로 질문을 던지고 답변을 기다립니다.
# ==========================================================================
@app.post("/api/chatbot")
async def chatbot_endpoint(request: ChatRequest):
    try:
        # 1. 자바에서 넘어온 사용자의 질문을 꺼냅니다.
        user_message = request.question
        
        # 2. PM님이 만든 챗봇 모듈을 실행하여 Gemini에게 답변을 받아옵니다.
        result = chatbot_module.get_chat_response(user_message)
        
        # 3. 🌟 통신 핵심: 자바 서버는 "answer"라는 이름의 키값을 기다리고 있습니다!
        # 모듈에서 "reply"로 받은 답변의 이름표를 "answer"로 바꿔서 자바에게 돌려줍니다.
        if "reply" in result:
            return {"answer": result["reply"]}
        else:
            return {"answer": f"서버 오류가 발생했습니다: {result.get('error')}"}
            
    except Exception as e:
        # 에러 발생 시 자바로 에러 내용을 전달하여 앱 화면에 띄워줍니다.
        return {"answer": f"AI 컨설턴트 연결 중 문제가 발생했습니다: {str(e)}"}


# ==========================================================================
# [API 2] 비전 AI 쓰레기 스캔 및 GPS 검증 (기존 코드)
# ==========================================================================
@app.post("/api/scan")
async def scan(
    lat: float = Form(...), 
    lon: float = Form(...), 
    userId: str = Form("회원"), 
    file: UploadFile = File(...)
):
    # 1. GPS 거리 검증 (에러를 내뿜지 않고 valid 변수에 결과만 저장!)
    valid, dist = is_within_range(lat, lon)
    
    # 2. 전송받은 이미지를 서버의 임시 파일로 저장
    file_path = f"temp_{file.filename}"
    with open(file_path, "wb") as f:
        f.write(await file.read())
    
    # 3. 무조건 AI 분석 먼저 실행 (사용자 맞춤형 인사말을 위해 userId 전달)
    ai_result = analyze_trash(file_path, user_id=userId)
    
    # 4. 분석 결과 찌꺼기 청소 및 GPS 조건 덮어쓰기
    try:
        if isinstance(ai_result, str):
            # Gemini가 가끔 붙여주는 ```json 마크다운 찌꺼기 제거 (안전한 파싱을 위한 핵심 방어!)
            clean_json = ai_result.replace("```json", "").replace("```", "").strip()
            result_dict = json.loads(clean_json)
        else:
            result_dict = ai_result
            
        # 🌟 GPS 검증 로직: 수거장 20m 밖에 있다면 AI가 보상을 주라고 했어도 강제로 자격 박탈!
        if not valid:
            result_dict["is_reward_eligible"] = False
            result_dict["point_reason"] = "수거장 반경 20m를 벗어나 포인트가 지급되지 않습니다."
            
        return result_dict
        
    except Exception as e:
        print("🚨 JSON 파싱 에러:", e)
        # 파싱에 실패하더라도 서버가 터지지 않고 원본 문자열이라도 반환하도록 방어
        return ai_result


# ==========================================================================
# [API 3] 일일 OX 퀴즈 생성 (기존 코드)
# 추후 자바의 QuizController가 이 주소를 호출하여 3문제를 가져갑니다.
# ==========================================================================
@app.get("/api/quiz")
async def get_quiz():
    # 🌟 괄호 안에 숫자 0을 넣어주세요! (임시로 횟수 0을 넘겨주어 에러 방지)
    return generate_random_quiz(0)


# ==========================================================================
# 서버 실행 부스터 (이 파일 자체를 실행할 때 작동)
# ==========================================================================
if __name__ == "__main__":
    # host="0.0.0.0": 외부(자바 서버 등)에서의 접속을 모두 허용합니다.
    uvicorn.run(app, host="0.0.0.0", port=8000)