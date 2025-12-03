#!/bin/bash

# This is a placeholder script for deploying the financial analysis agent to Google Cloud Run.
# In a real-world scenario, you would replace the placeholder values with your actual GCP project details.

# Exit immediately if a command exits with a non-zero status.
set -e

# Define variables
PROJECT_ID="your-gcp-project-id"
SERVICE_NAME="financial-analysis-agent"
REGION="your-gcp-region"
IMAGE_NAME="gcr.io/${PROJECT_ID}/${SERVICE_NAME}:latest"

# Build the Docker image
echo "Building Docker image for ${SERVICE_NAME}..."
docker build -f financial_analysis_agent/Dockerfile . -t ${IMAGE_NAME}

# Push the image to Google Container Registry
echo "Pushing Docker image to GCR..."
gcloud auth configure-docker
docker push ${IMAGE_NAME}

# Deploy to Cloud Run
echo "Deploying ${SERVICE_NAME} to Cloud Run..."
gcloud run deploy ${SERVICE_NAME} \
  --image=${IMAGE_NAME} \
  --platform=managed \
  --region=${REGION} \
  --allow-unauthenticated \
  --project=${PROJECT_ID}
  # You would also configure secrets, environment variables, and IAM settings here.
  # For example:
  # --set-env-vars="REDIS_HOST=your-redis-host,REDIS_PORT=your-redis-port"
  # --set-secrets="ALPHA_VANTAGE_API_KEY=alpha-vantage-api-key:latest"

echo "Deployment of ${SERVICE_NAME} complete."

