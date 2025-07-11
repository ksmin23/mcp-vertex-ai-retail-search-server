# server.py
import os
from dotenv import load_dotenv
from fastmcp import FastMCP
from google.api_core.exceptions import InvalidArgument
from google.cloud import retail_v2

# .env 파일에서 환경 변수 로드
load_dotenv()

# --- Google Cloud 설정 ---
PROJECT_ID = os.getenv("PROJECT_ID")
LOCATION = os.getenv("LOCATION", "global")  # 기본값은 'global'
CATALOG_ID = os.getenv("CATALOG_ID")
SERVING_CONFIG_ID = os.getenv("SERVING_CONFIG_ID", "default_serving_config") # 기본 서빙 구성

# 필수 환경 변수 확인
if not all([PROJECT_ID, LOCATION, CATALOG_ID, SERVING_CONFIG_ID]):
    raise ValueError(
        "다음 환경 변수를 .env 파일에 설정해야 합니다: "
        "PROJECT_ID, LOCATION, CATALOG_ID, SERVING_CONFIG_ID"
    )

# API 호출을 위한 Placement 문자열 구성
placement = (
    f"projects/{PROJECT_ID}/locations/{LOCATION}/"
    f"catalogs/{CATALOG_ID}/servingConfigs/{SERVING_CONFIG_ID}"
)

# --- FastMCP 서버 설정 ---
mcp = FastMCP(
    "Vertex AI Search for Retail API",
    "소매업을 위한 Vertex AI Search를 사용하여 제품 카탈로그를 검색하는 에이전트입니다."
)

@mcp.tool
def search_products(query: str, visitor_id: str = "guest-user") -> list[dict]:
    """
    Searches the product catalog for a given query and returns the detailed information for each product found.

    Args:
        query (str): The product keyword to search for (e.g., "jeans", "sneakers").
        visitor_id (str): A unique ID to identify the user, used for personalized results.

    Returns:
        list[dict]: A list of dictionaries containing the full details of the found products.
    """
    try:
        search_client = retail_v2.SearchServiceClient()
        product_client = retail_v2.ProductServiceClient()  # 제품 정보 조회를 위한 클라이언트

        search_request = retail_v2.SearchRequest(
            placement=placement,
            query=query,
            visitor_id=visitor_id,
            page_size=5,  # 반환할 결과 수를 5개로 제한
        )
        
        print(f"Vertex AI Search 요청: {search_request}")
        
        search_response = search_client.search(request=search_request)
        
        print(f"Vertex AI Search 응답: {search_response}")

        results = []
        for result in search_response.results:
            # 검색 결과에서 제품의 전체 리소스 이름을 가져옵니다.
            product_name = result.product.name
            print(f"상세 정보��� 조회할 제품: {product_name}")

            # ProductServiceClient를 사용하여 제품의 전체 상세 정보를 가져옵니다.
            product_detail = product_client.get_product(name=product_name)
            
            # 상세 정보를 딕셔너리로 변환하여 결과 목록에 추가합니다.
            product_dict = retail_v2.Product.to_dict(product_detail)
            results.append(product_dict)
            
        return results

    except InvalidArgument as e:
        print(f"API 호출 오류: {e}")
        return {"error": "잘못된 인자입니다. serving config를 확인하세요.", "details": str(e)}
    except Exception as e:
        print(f"예상치 못한 오류: {e}")
        return {"error": "제품 검색 중 오류가 발생했습니다.", "details": str(e)}


if __name__ == "__main__":
    print("Vertex AI Search for Retail MCP 서버를 시작합니다.")
    print(f"설정된 Placement: {placement}")
    mcp.run()