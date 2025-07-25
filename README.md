# Vertex AI Search for Commerce MCP Server

This project is a Model Context Protocol (MCP) server example that provides the [Vertex AI Search for Commerce](https://cloud.google.com/retail) API from Google Cloud as a tool, using [FastMCP](https://github.com/fastmcp/fastmcp-py).

Through this server, an AI agent can search a product catalog using natural language queries.

## Key Features

-   Lightweight MCP server based on FastMCP
-   Provides Vertex AI Search for Commerce product search functionality (`search_products`)
-   Easy setup using a `.env` file

## Prerequisites

-   Python 3.8 or higher
-   [uv](https://github.com/astral-sh/uv) (a fast Python package installer and virtual environment manager)
-   [Google Cloud CLI](https://cloud.google.com/sdk/docs/install) (`gcloud`)

## Installation and Setup

1.  **Google Cloud Authentication**

    Set up Application Default Credentials (ADC) to access Google Cloud services from your local environment. Run the command below in your terminal and complete the authentication through your browser.

    ```bash
    gcloud auth application-default login
    ```

2.  **Environment Variable Setup**

    Copy the `.env.example` file in the project root directory to a new `.env` file, then modify the contents to match your Google Cloud environment.

    ```bash
    cp .env.example .env
    ```

    **`.env` file contents:**
    ```
    PROJECT_ID="your-gcp-project-id"
    LOCATION="global"
    CATALOG_ID="default_catalog"
    SERVING_CONFIG_ID="default_serving_config"
    ```

3.  **Create Virtual Environment and Install Dependencies**

    Use `uv` to create a virtual environment and install the necessary libraries.

    ```bash
    # Create virtual environment
    uv venv

    # Activate virtual environment (macOS/Linux)
    source .venv/bin/activate
    # (Windows: .venv\Scripts\activate)

    # Install dependencies
    uv pip install -r requirements.txt
    ```

## Running the Server

You can run the Python script directly using `uv`'s execution feature.

```bash
uv run python src/server.py
```

### Running the Server (using fastmcp)

You can also run the server using the CLI provided by the `fastmcp` library. This method automatically finds and runs the `FastMCP` instance.

Specify the module path where the `mcp` instance is located. You can use the `--port` option to specify a different port instead of the default (8080).

```bash
fastmcp run src/server.py --transport http --port 9000
```

When the server starts successfully, you will see a message like this:
```
INFO:     Started server process [12345]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:9000 (Press CTRL+C to quit)
```

## Provided Tools

This MCP server provides the following tool:

### `search_products`

-   **Description**: Searches for products in the product catalog based on a given query. For detailed information on filtering and ordering, see the [official documentation](https://cloud.google.com/retail/docs/filter-and-order).
-   **Parameters**:
    -   `query` (str): The product keyword to search for (e.g., "jeans", "sneakers").
    -   `visitor_id` (str, optional): A unique ID to identify the user. Used for personalized search results. (Default: "guest-user")
    -   `brand` (str, optional): Brand to filter by.
    -   `color_families` (str, optional): Color family to filter by.
    -   `category` (str, optional): Category to filter by.
    -   `size` (str, optional): Size to filter by.
    -   `page_size` (int): The number of results to return per page. (Default: 10)
-   **Returns**: A stream of dictionaries, where each dictionary contains the full details of a found product.

---

## Google Cloud Run Deployment Guide

This section guides you on how to deploy the MCP server to Google Cloud Run.

### 1. Prerequisites

This setup is for interacting with Google Cloud from your local machine.

-   **Install Google Cloud SDK**: If you don't have the `gcloud` CLI installed, refer to the [official documentation](https://cloud.google.com/sdk/docs/install) to install it.

-   **gcloud Authentication**:
    ```bash
    gcloud auth login
    ```

-   **Set Google Cloud Project**:
    ```bash
    gcloud config set project [YOUR_PROJECT_ID]
    ```
    *(Replace `[YOUR_PROJECT_ID]` with your actual GCP project ID.)*

-   **Enable Required APIs**:
    ```bash
    gcloud services enable run.googleapis.com \
        artifactregistry.googleapis.com
    ```

-   **Configure Docker Authentication**:
    ```bash
    gcloud auth configure-docker [REGION]-docker.pkg.dev
    ```
    *(Replace `[REGION]` with a GCP region like `asia-northeast3`.)*

### 2. Create a Dockerfile

Create a `Dockerfile` in the project root. This file defines how to containerize the application.

```Dockerfile
# 1. Set the base image
FROM python:3.11-slim

# 2. Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# 3. Set the working directory
WORKDIR /app

# 4. Install dependencies
COPY requirements.txt .
RUN pip install uv && uv pip install --no-cache -r requirements.txt

# 5. Copy source code
COPY . .

# 6. Expose the port
EXPOSE 8080

# 7. Run the application
# Use the fastmcp CLI to run the server in a production environment.
CMD ["fastmcp", "run", "src/server.py", "--transport", "http", "--host", "0.0.0.0", "--port", "8080"]
```
**Note**: Since we are using `fastmcp`, ensure that `fastmcp` is included in your `requirements.txt`.

### 3. Create an Artifact Registry Repository

Create a repository in Artifact Registry to store your Docker images.

```bash
gcloud artifacts repositories create [REPOSITORY_NAME] \
    --repository-format=docker \
    --location=[REGION] \
    --description="MCP Search Server repository"
```
-   `[REPOSITORY_NAME]`: Specify a desired repository name, such as `mcp-repo`.
-   `[REGION]`: Use the same region as in the previous step.

### 4. Build and Push the Image

There are two ways to build the container image and push it to Artifact Registry.

#### Method 1: Using Local Docker

This method requires Docker to be installed on your local machine.

```bash
# 1. Build the image
docker build -t [REGION]-docker.pkg.dev/[YOUR_PROJECT_ID]/[REPOSITORY_NAME]/mcp-vertexai-retail-search-server:latest .

# 2. Push the image
docker push [REGION]-docker.pkg.dev/[YOUR_PROJECT_ID]/[REPOSITORY_NAME]/mcp-vertexai-retail-search-server:latest
```
*(Replace `[REGION]`, `[YOUR_PROJECT_ID]`, and `[REPOSITORY_NAME]` with your actual values.)*

---

#### Method 2: Using Google Cloud Build (Recommended)

This method does not require a local Docker installation and uses Google Cloud's managed build service for faster and more reliable image building and pushing.

Run the following single command from your project root directory:

```bash
gcloud builds submit --tag [REGION]-docker.pkg.dev/[YOUR_PROJECT_ID]/[REPOSITORY_NAME]/mcp-vertexai-retail-search-server:latest .
```
*(Replace `[REGION]`, `[YOUR_PROJECT_ID]`, and `[REPOSITORY_NAME]` with your actual values.)*

This command sends the source code from the current directory to Cloud Build, builds the image using the `Dockerfile`, and saves it to Artifact Registry with the specified tag, automating the entire process.

### 5. Deploy to Cloud Run

When deploying to Cloud Run, it's a best practice to use a dedicated service account to grant the service the minimum permissions required. This enhances security by following the principle of least privilege.

#### Using a Service Account

1.  **Create a Service Account**:
    First, create a new service account for your Cloud Run service.

    ```bash
    gcloud iam service-accounts create mcp-vaisc-sa \
        --display-name="MCP Vertex AI Search for Commerce Service Account"
    ```
    - `mcp-vaisc-sa`: This is the ID of the service account. You can change it to your desired name.

2.  **Grant Permissions**:
    The service account needs permissions to access the Vertex AI Search for Commerce API. Grant the `Retail Viewer` role to the service account, which provides the necessary read-only permissions for searching products.

    ```bash
    gcloud projects add-iam-policy-binding [YOUR_PROJECT_ID] \
        --member="serviceAccount:mcp-vaisc-sa@[YOUR_PROJECT_ID].iam.gserviceaccount.com" \
        --role="roles/retail.viewer"
    ```
    - Replace `[YOUR_PROJECT_ID]` with your actual GCP project ID.

Now, you can deploy the service with this service account.

You can deploy the service in two ways: publicly accessible or restricted to a VPC.

#### Public Deployment

The following command deploys the service to be publicly accessible. The `--ingress all` setting is default, and `--allow-unauthenticated` permits public access.

```bash
gcloud run deploy mcp-vaisr-server \
    --image [REGION]-docker.pkg.dev/[YOUR_PROJECT_ID]/[REPOSITORY_NAME]/mcp-vertexai-retail-search-server:latest \
    --region [REGION] \
    --service-account "mcp-vaisc-sa@[YOUR_PROJECT_ID].iam.gserviceaccount.com" \
    --allow-unauthenticated
```
-   `--allow-unauthenticated`: This flag allows anyone to access the service. If authentication is required, remove this flag.


#### Secure Deployment within a VPC

To deploy the service so that it is only accessible from within a specific VPC network for enhanced security, use the `deploy_to_cloud_run.py` script. This script sets the ingress settings to `internal`, allowing access only from the specified VPC network.

```bash
python deploy_to_cloud_run.py --service-name internal-mcp-vaisr-server \
    --network [VPC] \
    --subnet [SUBNET] \
    --ingress internal \
    --vpc-egress all-traffic \
    --service-account "mcp-vaisc-sa@[YOUR_PROJECT_ID].iam.gserviceaccount.com"
```

For more details on Cloud Run ingress settings, refer to the [official documentation](https://cloud.google.com/run/docs/securing/ingress?authuser=2).

Once the deployment is complete, you can access your application via the provided service URL.


### 6. Import Catalog Data to Vertex AI Search for Commerce

For instructions on how to import catalog data, please refer to the following guide:
[Import catalog data](https://github.com/GoogleCloudPlatform/python-docs-samples/tree/main/retail/interactive-tutorials#import-catalog-data)


---

## Reference

-  [Model Context Protocol (MCP) - Introduction](https://modelcontextprotocol.io/introduction)
-  [FastMCP - Quickstart](https://gofastmcp.com/getting-started/quickstart)
-  [MCP Tools Documentation](https://google.github.io/adk-docs/tools/mcp-tools/)
-  [MCP Inspector](https://modelcontextprotocol.io/docs/tools/inspector): an interactive developer tool for testing and debugging MCP servers
-  [Importing Catalog Information to Vertex AI Search for Commerce](https://cloud.google.com/retail/docs/retail-api-tutorials#import_catalog_information)
    -  💻 [Sample Code on GitHub](https://github.com/GoogleCloudPlatform/python-docs-samples/tree/main/retail/interactive-tutorials/product)
-  [Searching for Products with Vertex AI Search for Commerce](https://cloud.google.com/retail/docs/retail-api-tutorials#search_tutorials)
    -  💻 [Sample Code on GitHub](https://github.com/GoogleCloudPlatform/python-docs-samples/tree/main/retail/interactive-tutorials/search)
