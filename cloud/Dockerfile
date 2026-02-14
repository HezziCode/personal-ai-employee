# Dockerfile for Platinum Tier Cloud Deployment
# Alternative to render.yaml for more control

FROM python:3.13-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy project code
COPY . .

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Environment defaults
ENV VAULT_PATH=./vault
ENV AGENT_MODE=cloud
ENV DRY_RUN=true
ENV PYTHONUNBUFFERED=1

# Start the cloud worker
CMD ["uvicorn", "cloud.cloud_worker:app", "--host", "0.0.0.0", "--port", "8000"]
