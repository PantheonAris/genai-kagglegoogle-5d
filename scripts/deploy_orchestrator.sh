#!/bin/bash

# This is a placeholder script for deploying the orchestrator to Google Cloud Run.
# In a real-world scenario, you would replace the placeholder values with your actual GCP project details.

# Exit immediately if a command exits with a non-zero status.
set -e

# Define variables
PROJECT_ID="your-gcp-project-id"
SERVICE_NAME="orchestrator"
REGION="your-gcp-region"
IMAGE_NAME="gcr.io/${PROJECT_ID}/${SERVICE_NAME}:latest"

# Build the Docker image
echo "Building Docker image for ${SERVICE_NAME}..."
docker build -f orchestrator/Dockerfile . -t ${IMAGE_NAME}

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
  --project=${PROJECT_ID} \
  # In a real deployment, you would set environment variables for the agent URLs.
  # These would be the URLs of the deployed budget and financial analysis agents.
  # --set-env-vars="BUDGET_AGENT_URL=https://budget-agent-your-hash-uc.a.run.app,FINANCIAL_ANALYSIS_AGENT_URL=https://financial-analysis-agent-your-hash-uc.a.run.app"
  # And you would set the secret for the Gemini API key.
  # --set-secrets="GEMINI_API_KEY=gemini-api-key:latest"

echo "Deployment of ${SERVICE_NAME} complete."
