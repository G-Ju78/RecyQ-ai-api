#!/bin/bash

# --- Private 서버 정보 ---
PRIVATE_HOST="10.1.2.6"          # 실제 Private 서버 IP
PRIVATE_USER="root"                 # Private 서버 계정
PRIVATE_KEY="/root/.ssh/id_rsa"     # Public 서버에서 Private 서버 접속용 키

# --- 실행 후 로그 남기기 ---
exec > /root/app/deploy_private.log 2>&1
echo "Starting deployment to Private server..."

# 현재 shell 세션에 SSH agent 등록 및 활성화
eval $(ssh-agent -s)
ssh-add $PRIVATE_KEY

# 원격 서버에 애플리케이션을 저장할 디렉토리(폴더) 생성
ssh -o StrictHostKeyChecking=no $PRIVATE_USER@$PRIVATE_HOST "mkdir -p /root/app"

# 로컬에서 빌드된 JAR 파일을 원격 서버의 /root/app/app.jar 로 복사
scp -o StrictHostKeyChecking=no /root/app/target/*.jar $PRIVATE_USER@$PRIVATE_HOST:/root/app/app.jar

# 애플리케이션을 백그라운드에서 실행하고 로그는 app.log에 저장
ssh -o StrictHostKeyChecking=no $PRIVATE_USER@$PRIVATE_HOST "nohup java -jar /root/app/app.jar \
--spring.config.location=/home/config/application.properties > /root/app/app.log 2>&1 &"

# 추가 배포 작업이 필요한 경우 실행
ssh -o StrictHostKeyChecking=no $PRIVATE_USER@$PRIVATE_HOST "bash < /root/deploy.sh"

# SSH 세션 종료 후 보안상 agent 종료
ssh-agent -k

echo "Deployment to Private server completed."