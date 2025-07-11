# server.py
import os
from dotenv import load_dotenv
from fastmcp import FastMCP
from google.api_core.exceptions import InvalidArgument
from google.cloud import retail_v2

# Load environment variables from .env file
load_dotenv()

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
        search_request = retail_v2.SearchRequest(
            placement=placement,
            query=query,
            visitor_id=visitor_id,
            page_size=5,  # Limit the number of results to 5
        )
        
        print(f"Vertex AI Search request: {search_request}")
        
        search_response = search_client.search(request=search_request)
        
        print(f"Vertex AI Search response: {search_response}")

        results = []
        for result in search_response.results:
            # Get the full resource name of the product from the search result.
            product_name = result.product.name
            print(f"Fetching details for product: {product_name}")

            # Use ProductServiceClient to get the full details of the product.
            product_detail = product_client.get_product(name=product_name)
            
            # Convert the detailed information to a dictionary and add it to the results list.
            product_dict = retail_v2.Product.to_dict(product_detail)
            results.append(product_dict)
            
        return results

    except InvalidArgument as e:
        print(f"API call error: {e}")
        return {"error": "Invalid argument. Please check your serving config.", "details": str(e)}
    except Exception as e:
        print(f"Unexpected error: {e}")
        return {"error": "An error occurred while searching for products.", "details": str(e)}


if __name__ == "__main__":
    print("Starting Vertex AI Search for Retail MCP server.")
    print(f"Placement set to: {placement}")
    mcp.run()
