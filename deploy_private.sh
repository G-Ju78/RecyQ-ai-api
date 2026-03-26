#!/bin/bash

# --- AI 서버 정보 ---
PRIVATE_HOST="10.1.2.7"              # 실제 AI 서버 사설 IP로 수정
PRIVATE_USER="root"                  # AI 서버 계정
PRIVATE_KEY="/root/.ssh/id_rsa"      # 퍼블릭 서버에서 AI 서버 접속용 키

# --- 퍼블릭 서버에서 남길 배포 로그 파일 ---
exec > /root/recyq-ai-api/deploy_private.log 2>&1
echo "Starting deployment to AI server..."

# SSH agent 실행
eval $(ssh-agent -s)

# 퍼블릭 서버에 저장된 AI 서버 접속용 개인키 등록
ssh-add $PRIVATE_KEY

# --- AI 서버에 프로젝트 폴더 생성 ---
ssh -o StrictHostKeyChecking=no $PRIVATE_USER@$PRIVATE_HOST "mkdir -p /root/recyq-ai-api"

# --- 퍼블릭 서버 -> AI 서버로 FastAPI 프로젝트 파일 복사 ---
scp -o StrictHostKeyChecking=no /root/recyq-ai-api/main.py $PRIVATE_USER@$PRIVATE_HOST:/root/recyq-ai-api/
scp -o StrictHostKeyChecking=no /root/recyq-ai-api/chatbot_module.py $PRIVATE_USER@$PRIVATE_HOST:/root/recyq-ai-api/
scp -o StrictHostKeyChecking=no /root/recyq-ai-api/vision_module.py $PRIVATE_USER@$PRIVATE_HOST:/root/recyq-ai-api/
scp -o StrictHostKeyChecking=no /root/recyq-ai-api/quiz_module.py $PRIVATE_USER@$PRIVATE_HOST:/root/recyq-ai-api/
scp -o StrictHostKeyChecking=no /root/recyq-ai-api/config.py $PRIVATE_USER@$PRIVATE_HOST:/root/recyq-ai-api/
scp -o StrictHostKeyChecking=no /root/recyq-ai-api/database.py $PRIVATE_USER@$PRIVATE_HOST:/root/recyq-ai-api/
scp -o StrictHostKeyChecking=no /root/recyq-ai-api/requirements.txt $PRIVATE_USER@$PRIVATE_HOST:/root/recyq-ai-api/

# --- AI 서버에서 FastAPI 실행 환경 준비 및 서버 재시작 ---
ssh -o StrictHostKeyChecking=no $PRIVATE_USER@$PRIVATE_HOST "
cd /root/recyq-ai-api && \
python3 -m venv venv && \
source venv/bin/activate && \
pip install -r requirements.txt && \
pkill -f 'uvicorn main:app' || true && \
nohup venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000 > /root/recyq-ai-api/app.log 2>&1 &
"

# --- 보안상 ssh-agent 종료 ---
ssh-agent -k

echo 'Deployment to AI server completed.'