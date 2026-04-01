# main.py
from fastapi import FastAPI, File, UploadFile, Form
from pydantic import BaseModel
from vision_module import analyze_trash
from quiz_module import generate_random_quiz
from database import is_within_range
import chatbot_module
import uvicorn
import json

app = FastAPI()

# [1] 챗봇 데이터를 받기 위한 모델 (자바의 RequestBody와 매칭)
class ChatRequest(BaseModel):
    question: str

# ==========================================================================
# [API 1] AI 챗봇 엔드포인트
# STS ChatbotController의 fastapiUrl = ".../api/chatbot" 과 일치시킴
# ==========================================================================
@app.post("/api/chatbot")
async def chatbot_endpoint(request: ChatRequest):
    try:
        user_message = request.question
        result = chatbot_module.get_chat_response(user_message)
        
        # 자바는 "answer"라는 키값을 기다리므로 이름을 맞춰서 반환
        if "reply" in result:
            return {"answer": result["reply"]}
        else:
            return {"answer": "AI 컨설턴트 응답 생성 실패"}
            
    except Exception as e:
        return {"answer": f"연결 오류: {str(e)}"}


# ==========================================================================
# [API 2] 비전 AI 스캔 엔드포인트 (기존 규격 유지)
# ==========================================================================
@app.post("/api/scan")
async def scan(
    lat: float = Form(...), 
    lon: float = Form(...), 
    userId: str = Form("회원"), 
    file: UploadFile = File(...)
):
    valid, dist = is_within_range(lat, lon)
    
    file_path = f"temp_{file.filename}"
    with open(file_path, "wb") as f:
        f.write(await file.read())
    
    ai_result = analyze_trash(file_path, user_id=userId)
    
    try:
        if isinstance(ai_result, str):
            clean_json = ai_result.replace("```json", "").replace("```", "").strip()
            result_dict = json.loads(clean_json)
        else:
            result_dict = ai_result
            
        if not valid:
            result_dict["is_reward_eligible"] = False
            result_dict["point_reason"] = "수거장 반경 20m를 벗어나 포인트가 지급되지 않습니다."
            
        return result_dict
    except Exception as e:
        return ai_result


# ==========================================================================
# [API 3] 일일 OX 퀴즈 엔드포인트
# STS QuizController의 fastapiUrl = ".../api/quiz" 와 100% 일치시킴
# (주의: 뒤에 /get을 붙이지 않습니다. 자바 코드에 /quiz까지만 적혀있기 때문입니다.)
# ==========================================================================
@app.get("/api/quiz")
async def get_quiz():
    # 퀴즈 모듈 호출 (인자 0은 임시 처리)
    return generate_random_quiz(0)


# ==========================================================================
# 서버 실행 (포트 8000번 고정)
# ==========================================================================
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)