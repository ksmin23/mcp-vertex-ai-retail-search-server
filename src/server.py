#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
# vim: tabstop=2 shiftwidth=2 softtabstop=2 expandtab

import os
import logging
from typing import Optional
from dotenv import load_dotenv
from fastmcp import FastMCP
from google.api_core.exceptions import InvalidArgument
from google.cloud import retail_v2

# Load environment variables from .env file
load_dotenv()

# --- Logger Setup ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- Google Cloud Settings ---
PROJECT_ID = os.getenv("PROJECT_ID")
LOCATION = os.getenv("LOCATION", "global")  # Default to 'global'
CATALOG_ID = os.getenv("CATALOG_ID")
SERVING_CONFIG_ID = os.getenv("SERVING_CONFIG_ID", "default_serving_config") # Default serving config

# Check for required environment variables
if not all([PROJECT_ID, LOCATION, CATALOG_ID, SERVING_CONFIG_ID]):
  raise ValueError(
    "The following environment variables must be set in the .env file: "
    "PROJECT_ID, LOCATION, CATALOG_ID, SERVING_CONFIG_ID"
  )

# Construct the placement string for API calls
placement = (
  f"projects/{PROJECT_ID}/locations/{LOCATION}/"
  f"catalogs/{CATALOG_ID}/servingConfigs/{SERVING_CONFIG_ID}"
)

# --- FastMCP Server Setup ---
mcp = FastMCP(
  "Vertex AI Search for Retail API",
  "A mcp server that searches a product catalog using Vertex AI Search for Retail."
)

# Initialize clients once to be reused in the function
search_client = retail_v2.SearchServiceClient()
product_client = retail_v2.ProductServiceClient()

@mcp.tool
def search_products(
    query: str,
    visitor_id: str = "guest-user",
    brand: Optional[str] = None,
    color_families: Optional[str] = None,
    category: Optional[str] = None,
    size: Optional[str] = None,
    page_size: int = 10,
):
  """
  Searches the product catalog for a given query and streams the detailed information for each product found.
  For detailed information on filtering and ordering with search, see: https://cloud.google.com/retail/docs/filter-and-order

  Args:
    query (str): The product keyword to search for (e.g., "jeans", "sneakers").
    visitor_id (str): A unique ID to identify the user, used for personalized results.
    brand (str, optional): Brand to filter by.
    color_families (str, optional): Color family to filter by.
    category (str, optional): Category to filter by.
    size (str, optional): Size to filter by.
    page_size (int): The number of results to return per page.

  Yields:
    dict: A dictionary containing the full details of each found product.
  """
  try:
    filter_conditions = []
    if brand:
        filter_conditions.append(f'(brand: ANY("{brand}"))')
    if color_families:
        filter_conditions.append(f'(colorFamilies: ANY("{color_families}"))')
    if category:
        filter_conditions.append(f'(categories: ANY("{category}"))')
    if size:
        filter_conditions.append(f'(sizes: ANY("{size}"))')

    filter_str = " AND ".join(filter_conditions) if filter_conditions else ""

    search_request = retail_v2.SearchRequest(
      placement=placement,
      query=query,
      visitor_id=visitor_id,
      filter=filter_str,
      page_size=page_size,
    )

    logger.debug(f"Vertex AI Search request: {search_request}")

    search_response = search_client.search(request=search_request)

    logger.debug(f"Vertex AI Search response: {search_response}")

    for result in search_response.results:
      # Get the full resource name of the product from the search result.
      product_name = result.product.name
      logger.info(f"Fetching details for product: {product_name}")

      # Use ProductServiceClient to get the full details of the product.
      product_detail = product_client.get_product(name=product_name)

      # Convert the detailed information to a dictionary and yield it.
      product_dict = retail_v2.Product.to_dict(product_detail)
      yield product_dict

  except InvalidArgument as e:
    logger.error(f"API call error: {e}")
    yield {"error": "Invalid argument. Please check your serving config.", "details": str(e)}
  except Exception as e:
    logger.error(f"Unexpected error: {e}")
    yield {"error": "An error occurred while searching for products.", "details": str(e)}


if __name__ == "__main__":
  logger.info("Starting Vertex AI Search for Retail MCP server.")
  logger.info(f"Placement set to: {placement}")
  mcp.run(transport="http")