FROM python:3.12-slim

WORKDIR /app

# 1. 의존성 먼저 복사 및 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 2. 로컬 모듈(wikipedia.py, osrm.py 등)을 모두 포함하여 전체 복사
COPY . .

EXPOSE 8000

CMD ["python", "server.py"]