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

## 설치 및 설정

1.  **Google Cloud 인증**

    로컬 환경에서 Google Cloud 서비스에 접근할 수 있도록 ADC(Application Default Credentials)를 설정합니다. 터미널에서 아래 명령어를 실행하고 브라우저를 통해 인증을 완료하세요.

    ```bash
    gcloud auth application-default login
    ```

2.  **환경 변수 설정**

    프로젝트 루트�� 있는 `.env.example` 파일을 `.env` 파일로 복사한 후, 파일 내용을 자신의 Google Cloud 환경에 맞게 수정합니다.

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
uv run python src/mcp_search_server/main.py
```

### 서버 실행 (fastmcp 사용)

`fastmcp` 라이브러리에서 제공하는 CLI를 사용하여 서버를 실행할 수도 있습니다. 이 방법은 `FastMCP` 인스턴스를 자동으로 찾아 실행해줍니다.

`mcp` 인스턴스가 위치한 모듈 경로를 지정하여 실행합니다. `--port` 옵션을 사용하여 기본 포트(8080) 대신 다른 포트를 지정할 수 있습니다.

```bash
uv run fastmcp run src/mcp_search_server/main.py --transport http --port 9000
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
-   **반환값**: 검색된 제품 목록 (각 제품은 `id`, `title`, `price`, `uri` 정보를 포함하는 딕셔너리).
