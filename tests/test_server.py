# tests/test_server.py
import os
import sys
import unittest
from unittest.mock import patch, MagicMock
from google.api_core.exceptions import InvalidArgument
from google.cloud import retail_v2

# Add the project root to sys.path to allow importing the 'server' module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Set environment variables for testing
os.environ['PROJECT_ID'] = 'test-project'
os.environ['LOCATION'] = 'global'
os.environ['CATALOG_ID'] = 'test-catalog'
os.environ['SERVING_CONFIG_ID'] = 'test-config'

from server import search_products, product_client

class TestSearchProducts(unittest.TestCase):

    @patch('server.retail_v2.SearchServiceClient')
    @patch('server.product_client', new_callable=MagicMock)
    def test_search_products_success_stream(self, mock_product_client, mock_search_client):
        """
        Tests if the search_products function successfully calls the API and streams the results.
        """
        # --- Mock Setup ---
        # Mock SearchServiceClient instance
        mock_search_instance = MagicMock()
        mock_search_client.return_value = mock_search_instance

        # Mock search API response
        mock_search_response = MagicMock()
        mock_search_result = MagicMock()
        mock_search_result.product.name = "projects/test-project/locations/global/catalogs/test-catalog/branches/0/products/test_id_123"
        mock_search_response.results = [mock_search_result]
        mock_search_instance.search.return_value = mock_search_response

        # Mock ProductServiceClient's get_product response
        mock_product_detail = retail_v2.Product(
            id="test_id_123",
            title="Test Product",
            price_info=retail_v2.PriceInfo(price=99.99),
            uri="http://example.com/product/123"
        )
        mock_product_client.get_product.return_value = mock_product_detail

        # --- Test Execution ---
        query = "test query"
        results_generator = search_products.func(query) # Convert generator to list to check results
        results = list(results_generator) # Convert generator to list to check results

        # --- Verification ---
        # 1. Verify that the search method was called with the correct arguments
        expected_placement = "projects/test-project/locations/global/catalogs/test-catalog/servingConfigs/test-config"
        mock_search_instance.search.assert_called_once()
        called_args, called_kwargs = mock_search_instance.search.call_args
        self.assertEqual(called_kwargs['request'].placement, expected_placement)
        self.assertEqual(called_kwargs['request'].query, query)

        # 2. Verify that get_product was called for the product in the search results
        mock_product_client.get_product.assert_called_once_with(name=mock_search_result.product.name)

        # 3. Verify that the returned results match expectations
        expected_results = [retail_v2.Product.to_dict(mock_product_detail)]
        self.assertEqual(results, expected_results)

    @patch('server.retail_v2.SearchServiceClient')
    def test_search_products_api_error(self, mock_search_client):
        """
        Tests that an error message is correctly returned when an API call exception occurs.
        """
        # --- Mock Setup ---
        mock_client_instance = MagicMock()
        mock_search_client.return_value = mock_client_instance
        mock_client_instance.search.side_effect = InvalidArgument("API call failed")

        # --- Test Execution ---
        results_generator = search_products.func("any query")
        results = list(results_generator)

        # --- Verification ---
        self.assertEqual(len(results), 1)
        self.assertIn("error", results[0])
        self.assertEqual(results[0]["error"], "Invalid argument. Please check your serving config.")

if __name__ == '__main__':
    unittest.main()
