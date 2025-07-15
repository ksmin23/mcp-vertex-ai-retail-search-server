# 1. 기본 이미지 설정
# Python 3.11의 가벼운 버전을 사용합니다.
FROM python:3.11-slim

# 2. 환경 변수 설정
# Python이 .pyc 파일을 생성하지 않도록 하고, 출력을 버퍼링 없이 바로 표시합니다.
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# 3. 작업 디렉토리 설정
WORKDIR /app

# 4. 의존성 설치
# requirements.txt를 먼저 복사하여 Docker 캐시를 활용합니다.
COPY requirements.txt .
# uv를 사용하여 의존성을 설치합니다.
RUN pip install uv && uv pip install --system --no-cache -r requirements.txt

# 5. 소스 코드 복사
COPY . .

# 6. 포트 노출
# Cloud Run은 기본적으로 8080 포트를 사용합니다.
EXPOSE 8080

# 7. 애플리케이션 실행
# fastmcp CLI를 사용하여 프로덕션 환경에서 서버를 실행합니다.
CMD ["fastmcp", "run", "src/server.py", "--transport", "streamable-http", "--host", "0.0.0.0", "--port", "8080"]
