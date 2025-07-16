# 1. Set the base image
# Use a lightweight version of Python 3.11.
FROM python:3.11-slim

# 2. Set environment variables
# Prevents Python from writing .pyc files and buffers output directly.
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# 3. Set the working directory
WORKDIR /app

# 4. Install dependencies
# Copy requirements.txt first to leverage Docker cache.
COPY requirements.txt .
# Install dependencies using uv.
RUN pip install uv && uv pip install --system --no-cache -r requirements.txt

# 5. Copy source code
COPY . .

# 6. Expose the port
# Cloud Run uses port 8080 by default.
EXPOSE 8080

# 7. Run the application
# Use the fastmcp CLI to run the server in a production environment.
CMD ["fastmcp", "run", "src/server.py", "--transport", "streamable-http", "--host", "0.0.0.0", "--port", "8080"]
