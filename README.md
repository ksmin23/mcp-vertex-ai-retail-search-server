# Vertex AI Search for Retail MCP 서버

이 프로젝트는 [FastMCP](https://github.com/fastmcp/fastmcp-py)를 사용하여 Google Cloud의 [Vertex AI Search for Retail](https://cloud.google.com/retail) API를 도구(Tool)로 제공하는 Model Context Protocol (MCP) 서버 예제입니다.

이 서버를 통해 AI 에이전트는 자연어 쿼리를 사용하여 제품 카탈로그를 검색할 수 있습니다.

## 주요 기능

-   FastMCP 기반의 경량 MCP 서버
-   Vertex AI Search for Retail 제품 검색 기능(`search_products`) 제공
-   `.env` 파일을 사용한 간편한 설정

## 사전 요구사항

-   Python 3.8 이상
-   [uv](https://github.com/astral-sh/uv) (빠른 Python 패키지 설치 및 가상 환경 관리 도구)
-   [Google Cloud CLI](https://cloud.google.com/sdk/docs/install) (`gcloud`)

## ��치 및 설정

1.  **Google Cloud 인증**

    로컬 환경에서 Google Cloud 서비스에 접근할 수 있도록 ADC(Application Default Credentials)를 설정합니다. 터미널에서 아래 명령어를 실행하고 브라우저를 통해 인증을 완료하세요.

    ```bash
    gcloud auth application-default login
    ```

2.  **환경 변수 설정**

    프로젝트 루트 디렉터리에 있는 `.env.example` 파일을 `.env` 파일로 복사한 후, 파일 내용을 자신의 Google Cloud 환경에 맞게 수정합니다.

    ```bash
    cp .env.example .env
    ```

    **`.env` 파일 내용:**
    ```
    PROJECT_ID="your-gcp-project-id"
    LOCATION="global"
    CATALOG_ID="default_catalog"
    SERVING_CONFIG_ID="default_serving_config"
    ```

3.  **가상 환경 생성 및 의존성 설치**

    `uv`를 사용하여 가상 환경을 만들고 필요한 라이브러리를 설치합니다.

    ```bash
    # 가상 환경 생성
    uv venv

    # 가상 환경 활성화 (macOS/Linux)
    source .venv/bin/activate
    # (Windows: .venv\Scripts\activate)

    # 의존성 설치
    uv pip install -r requirements.txt
    ```

## 서버 실행

`uv`의 실행 기능을 사용하여 Python 스크립트를 직접 실행할 수 있습니다.

```bash
uv run python src/server.py
```

### 서버 실행 (fastmcp 사용)

`fastmcp` 라이브러리에서 제공하는 CLI를 사용하여 서버를 실행할 수도 있습니다. 이 방법은 `FastMCP` 인스턴스를 자동으로 찾아 실행해줍니다.

`mcp` 인스턴스가 위치한 모듈 경로를 지정하여 실행합니다. `--port` 옵션을 사용하여 기본 포트(8080) 대신 다른 포트를 지정할 수 있습니다.

```bash
uv run fastmcp run src/server.py --transport http --port 9000
```

서버가 정상적으로 시작되면 다음과 같은 메시지가 출력됩니다.
```
INFO:     Started server process [12345]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:9000 (Press CTRL+C to quit)
```

## 제공되는 도구

이 MCP 서버는 다음과 같은 도구를 제공합니다.

### `search_products`

-   **설명**: 제품 카탈로그에서 주어진 검색어로 제품을 검색합니다.
-   **매개변수**:
    -   `query` (str): 검색할 제품 키워드 (예: "청바지", "운동화").
    -   `visitor_id` (str, 선택 사항): 사용자를 식별하는 고유 ID. 개인화된 검색 결과에 사용됩니다. (기본값: "guest-user")
-   **반환값**: 검색된 제품 목록 (각 제품은 `id`, `title`, `price`, `uri` 정보를 포���하는 딕셔너리).

---

## Google Cloud Run 배포 안내

이 섹션에서는 MCP 서버를 Google Cloud Run에 배포하는 방법을 안내합니다.

### 1. 사전 준비

로컬 머신에서 Google Cloud와 상호작용하기 위한 설정입니다.

-   **Google Cloud SDK 설치**: `gcloud` CLI가 설치되어 있지 않다면 [공식 문서](https://cloud.google.com/sdk/docs/install)를 참고하여 설치합니다.

-   **gcloud 인증**:
    ```bash
    gcloud auth login
    ```

-   **Google Cloud 프로젝트 설정**:
    ```bash
    gcloud config set project [YOUR_PROJECT_ID]
    ```
    *(`[YOUR_PROJECT_ID]`를 실제 GCP 프로젝트 ID로 변경하세요.)*

-   **필요한 API 활성화**:
    ```bash
    gcloud services enable run.googleapis.com \
        artifactregistry.googleapis.com
    ```

-   **Docker 인증 설정**:
    ```bash
    gcloud auth configure-docker [REGION]-docker.pkg.dev
    ```
    *(`[REGION]`을 `asia-northeast3`와 같은 GCP 리전으로 변경하세요.)*

### 2. Dockerfile 생성

프로젝트 루트에 `Dockerfile`을 생성합니다. 이 파일은 애플리케이션을 컨테이너화하는 방법을 정의합니다.

```Dockerfile
# 1. 기본 이미지 설정
FROM python:3.11-slim

# 2. 환경 변수 설정
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# 3. 작업 디렉토리 설정
WORKDIR /app

# 4. 의존성 설치
COPY requirements.txt .
RUN pip install uv && uv pip install --no-cache -r requirements.txt

# 5. 소스 코드 복사
COPY . .

# 6. 포트 노출
EXPOSE 8080

# 7. 애플리케이션 실행
# fastmcp CLI를 사용하여 프로덕션 환경에서 서버를 실행합니다.
CMD ["fastmcp", "run", "src/server.py", "--transport", "http", "--host", "0.0.0.0", "--port", "8080"]
```
**참고**: `fastmcp`을 사용하므로, `requirements.txt`에 `fastmcp`이 포함되어 있는지 확인하세요.

### 3. Artifact Registry 저장소 생성

Docker 이미지를 저장할 Artifact Registry 저장소를 생성합니다.

```bash
gcloud artifacts repositories create [REPOSITORY_NAME] \
    --repository-format=docker \
    --location=[REGION] \
    --description="MCP Search Server repository"
```
-   `[REPOSITORY_NAME]`: `mcp-repo`와 같이 원하는 저장소 이름을 지정합니다.
-   `[REGION]`: 이전 단계에서 사용한 리전과 동일하게 지정합니다.

### 4. 이미지 빌드 및 푸시

컨테이너 이미지를 빌드하고 Artifact Registry에 푸시하는 방법은 두 가지가 있습니다.

#### 방법 1: 로컬 Docker 사용

이 방법은 로컬 컴퓨터에 Docker가 설치되어 있어야 합니다.

```bash
# 1. 이미지 빌드
docker build -t [REGION]-docker.pkg.dev/[YOUR_PROJECT_ID]/[REPOSITORY_NAME]/mcp-vertexai-retail-search-server:latest .

# 2. 이미지 푸시
docker push [REGION]-docker.pkg.dev/[YOUR_PROJECT_ID]/[REPOSITORY_NAME]/mcp-vertexai-retail-search-server:latest
```
*(`[REGION]`, `[YOUR_PROJECT_ID]`, `[REPOSITORY_NAME]`을 실제 값으로 변경하세요.)*

---

#### 방법 2: Google Cloud Build 사용 (권장)

이 방법은 로컬에 Docker를 설치할 필요가 없으며, Google Cloud의 관리형 빌드 서비스를 사용하여 더 빠르고 안정적으로 이미지를 빌드하고 푸시합니다.

프로젝트 루트 디렉터리에서 다음 단일 명령어를 실행하세요.

```bash
gcloud builds submit --tag [REGION]-docker.pkg.dev/[YOUR_PROJECT_ID]/[REPOSITORY_NAME]/mcp-vertexai-retail-search-server:latest .
```
*(`[REGION]`, `[YOUR_PROJECT_ID]`, `[REPOSITORY_NAME]`을 실제 값으로 변경하세요.)*

이 명령어는 현재 디렉터리의 소스 코드를 Cloud Build로 전송하고, `Dockerfile`을 사용하여 이미지를 빌드한 후, 지정된 태그로 Artifact Registry에 저장까지 모든 과정을 자동으로 처리합니다.

### 5. Cloud Run 배포

푸시된 이미지를 사용하여 Cloud Run 서비스를 배포합니다.

```bash
gcloud run deploy mcp-vaisr-server \
    --image [REGION]-docker.pkg.dev/[YOUR_PROJECT_ID]/[REPOSITORY_NAME]/mcp-vertexai-retail-search-server:latest \
    --region [REGION] \
    --network [VPC] \
    --subnet [SUBNET] \
    --allow-unauthenticated
```
-   `--allow-unauthenticated`: 이 플래그는 누구나 서비스에 접근할 수 있도록 허용합니다. 인증이 필요한 경우 이 플래그를 제거하세요.

배포가 완료되면 출력된 서비스 URL을 통해 애플리케이션에 접근할 수 있습니다.