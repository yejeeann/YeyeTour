# 1. Base Image: Python 3.11 공식 이미지를 기반으로 합니다.
FROM python:3.11-slim

# 2. Working Directory: 컨테이너 내 작업 디렉토리를 설정합니다.
WORKDIR /app

# 3. Copy & Install Dependencies: 먼저 의존성 파일을 복사하고 설치합니다.
#    (소스 코드가 변경되어도 이 부분은 캐시를 통해 재사용되어 빌드 속도가 향상됩니다.)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. Copy Source Code: 나머지 소스 코드를 컨테이너에 복사합니다.
COPY . .

# 5. Expose Port: FastAPI 기본 포트인 8000번을 외부에 노출하도록 설정합니다.
EXPOSE 8000

# 6. Run Command: 컨테이너가 시작될 때 실행할 명령어를 정의합니다.
#    Uvicorn을 사용하여 0.0.0.0 호스트로 서버를 실행, 외부 요청을 수신할 수 있게 합니다.
CMD ["uvicorn", "server:mcp_app", "--host", "0.0.0.0", "--port", "8000"]
