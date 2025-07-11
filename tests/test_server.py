# tests/test_server.py
import os
import sys
import unittest
from unittest.mock import patch, MagicMock

# 프로젝트 루트를 sys.path에 추가하여 'server' 모듈을 임포트할 수 있도록 함
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# 테스트를 위한 환경 변수 설정
os.environ['PROJECT_ID'] = 'test-project'
os.environ['LOCATION'] = 'global'
os.environ['CATALOG_ID'] = 'test-catalog'
os.environ['SERVING_CONFIG_ID'] = 'test-config'

from server import search_products

class TestSearchProducts(unittest.TestCase):

    @patch('server.retail_v2.SearchServiceClient')
    def test_search_products_success(self, mock_search_client):
        """
        search_products 함수가 성공적으로 API를 호출하고 결과를 파싱하는지 테스트합니다.
        """
        # --- Mock 설정 ---
        # SearchServiceClient 인스턴스 모의 처리
        mock_client_instance = MagicMock()
        mock_search_client.return_value = mock_client_instance

        # API 응답 모의 처리
        mock_response = MagicMock()
        mock_result = MagicMock()
        mock_product = mock_result.product
        mock_product.id = "test_id_123"
        mock_product.title = "Test Product"
        mock_product.price_info.price = 99.99
        mock_product.uri = "http://example.com/product/123"
        
        mock_response.results = [mock_result]
        mock_client_instance.search.return_value = mock_response

        # --- 테스트 실행 ---
        query = "test query"
        results = search_products(query)

        # --- 검증 ---
        # 1. search 메서드가 올바른 인자와 함께 호출되었는지 확인
        expected_placement = "projects/test-project/locations/global/catalogs/test-catalog/servingConfigs/test-config"
        mock_client_instance.search.assert_called_once()
        called_args, called_kwargs = mock_client_instance.search.call_args
        self.assertEqual(called_kwargs['request'].placement, expected_placement)
        self.assertEqual(called_kwargs['request'].query, query)

        # 2. 반환된 결과가 예상과 일치하는지 확인
        expected_results = [{
            "id": "test_id_123",
            "title": "Test Product",
            "price": 99.99,
            "uri": "http://example.com/product/123"
        }]
        self.assertEqual(results, expected_results)

    @patch('server.retail_v2.SearchServiceClient')
    def test_search_products_api_error(self, mock_search_client):
        """
        API 호출 시 예외가 발생했을 때 에러 메시지를 올바르게 반환하는지 테스트합니다.
        """
        # --- Mock 설정 ---
        mock_client_instance = MagicMock()
        mock_search_client.return_value = mock_client_instance
        mock_client_instance.search.side_effect = Exception("API call failed")

        # --- 테스트 실행 ---
        results = search_products("any query")

        # --- 검증 ---
        self.assertIn("error", results)
        self.assertEqual(results["error"], "제품 검색 중 오류가 발생했습니다.")

if __name__ == '__main__':
    unittest.main()
