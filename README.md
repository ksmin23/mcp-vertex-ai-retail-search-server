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

-   **Description**: Searches for products in the product catalog based on a given query.
-   **Parameters**:
    -   `query` (str): The product keyword to search for (e.g., "jeans", "sneakers").
    -   `visitor_id` (str, optional): A unique ID to identify the user. Used for personalized search results. (Default: "guest-user")
-   **Returns**: A list of searched products (each product is a dictionary containing `id`, `title`, `price`, and `uri` information).

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

Deploy the pushed image as a Cloud Run service.

```bash
gcloud run deploy mcp-vaisr-server \
    --image [REGION]-docker.pkg.dev/[YOUR_PROJECT_ID]/[REPOSITORY_NAME]/mcp-vertexai-retail-search-server:latest \
    --region [REGION] \
    --network [VPC] \
    --subnet [SUBNET] \
    --allow-unauthenticated
```
-   `--allow-unauthenticated`: This flag allows anyone to access the service. If authentication is required, remove this flag.

Once the deployment is complete, you can access your application via the provided service URL.

---

## Reference

-   [Model Context Protocol (MCP) - Introduction](https://modelcontextprotocol.io/introduction)
-   [FastMCP - Quickstart](https://gofastmcp.com/getting-started/quickstart)
-   [MCP Tools Documentation](https://google.github.io/adk-docs/tools/mcp-tools/)
