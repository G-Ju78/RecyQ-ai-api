from fastapi import FastAPI, File, UploadFile, Form
from pydantic import BaseModel
from vision_module import analyze_trash  # 비전 모듈 (기존)
from quiz_module import generate_random_quiz  # 퀴즈 모듈 (기존)
from database import is_within_range
import chatbot_module  # ✅ 위에서 만든 챗봇 모듈 import
import uvicorn
import json

app = FastAPI()

# [1] 자바에서 보낸 JSON 데이터를 담을 바구니
class ChatRequest(BaseModel):
    question: str

# [2] 챗봇 API 엔드포인트
@app.post("/api/chatbot")
async def chatbot_endpoint(request: ChatRequest):
    try:
        # 자바에서 넘어온 질문 추출
        user_message = request.question
        
        # ✅ chatbot_module의 수정된 로직 실행
        result = chatbot_module.get_chat_response(user_message)
        
        # ✅ 자바 서버는 "answer"라는 키값을 기다리므로 이름 변경해서 반환
        if "reply" in result:
            return {"answer": result["reply"]}
        else:
            return {"answer": f"AI 컨설턴트 답변 생성 중 오류가 발생했습니다."}
            
    except Exception as e:
        return {"answer": f"연결 오류: {str(e)}"}

# [3] 비전 AI 스캔 API (기존 틀 유지)
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
    
    # 비전 분석 호출 (수정된 2.5 flash 모델 적용된 버전이어야 함)
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

# 서버 실행
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)