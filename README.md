# Multi-Agent Financial Advisory System

This project implements a multi-agent financial advisory system designed to provide personalized financial advice. It orchestrates specialized AI agents using Google Gemini to address various financial needs, from budgeting to investment analysis.

## 🚀 Features

*   **Intelligent Orchestration**: Dynamically routes user queries to the most appropriate specialized agent based on identified intent.
*   **Budgeting Tools**:
    *   **50/30/20 Rule Calculator**: Helps users allocate income into Needs, Wants, and Savings.
    *   **Spending Analyzer**: Provides insights into spending habits and offers actionable recommendations.
*   **Financial Analysis Tools**:
    *   **Stock Data Retrieval**: Fetches real-time and historical stock data from multiple providers.
    *   **Portfolio Recommendation**: Suggests diversified investment portfolios based on user risk tolerance.
    *   **Stock Comparison**: Compares the historical performance of multiple stocks.
*   **Session Management**: Maintains conversational context and user-specific data using Redis.
*   **Structured Logging**: Integrates `structlog` for enhanced observability across all services.
*   **Containerized Services**: Each agent is an independent, containerized service for scalable deployment on Cloud Run.

## 🛠️ Technology Stack

*   **Cloud Platform**: Google Cloud Platform (GCP)
*   **Backend Framework**: Python 3.10+ with FastAPI
*   **AI/LLM**: Google Gemini Pro (via `google-generativeai` SDK)
*   **Deployment**: Google Cloud Run
*   **Session State**: Google Cloud Memorystore (Redis)
*   **Secrets Management**: Google Secret Manager
*   **HTTP Client**: `httpx` for internal service-to-service communication
*   **Financial Data Providers**: Alpha Vantage, Yahoo Finance (via `yfinance` library)
*   **Logging**: `structlog`
*   **Dependency Management**: `pip` and `pyproject.toml`

## 🏗️ Project Structure

The project is organized as a monorepo, with each core component residing in its own service directory.

```
.
├── budget_agent/             # Contains the Budget Agent service
│   ├── main.py               # FastAPI application for budget calculations
│   ├── schemas.py            # Pydantic models for request/response
│   ├── Dockerfile            # Dockerfile for containerization
│   └── pyproject.toml        # Project dependencies and metadata
├── financial_analysis_agent/ # Contains the Financial Analysis Agent service
│   ├── main.py               # FastAPI application for financial analysis
│   ├── schemas.py            # Pydantic models for request/response
│   ├── clients/              # Data provider clients (Alpha Vantage, Yahoo Finance)
│   ├── services/             # Business logic services (FinancialDataService, PortfolioService)
│   ├── utils/                # Utility functions (e.g., caching)
│   ├── Dockerfile            # Dockerfile for containerization
│   └── pyproject.toml        # Project dependencies and metadata
├── orchestrator/             # Contains the Orchestrator Agent service
│   ├── main.py               # FastAPI application for intent recognition, delegation, and synthesis
│   ├── clients.py            # Internal service-to-service communication client
│   ├── session.py            # Redis-based session management
│   ├── gemini.py             # Gemini API client and prompt handling
│   ├── prompts.py            # Stores AI prompts (intent recognition, response synthesis)
│   ├── Dockerfile            # Dockerfile for containerization
│   └── pyproject.toml        # Project dependencies and metadata
├── scripts/                  # Deployment scripts for each service
│   ├── deploy_budget_agent.sh
│   ├── deploy_financial_analysis_agent.sh
│   └── deploy_orchestrator.sh
├── .github/workflows/        # GitHub Actions CI/CD workflows
│   └── ci.yml                # Basic CI pipeline (lint, test, build)
├── README.md                 # This file
└── ...                       # Other project files (e.g., design docs, requirements)
```

## 🚀 Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites

*   Python 3.10+
*   Docker
*   `gcloud CLI` (for GCP deployment)
*   A Google Cloud Project with billing enabled
*   Enabled GCP APIs: Cloud Run, Secret Manager, Memorystore (Redis), IAM, Cloud Build, Artifact Registry
*   A dedicated GCP service account with appropriate least-privilege IAM roles (e.g., Cloud Run Invoker/Developer, Secret Manager Secret Accessor).
*   A Memorystore (Redis) instance provisioned.
*   API Keys for Gemini, Alpha Vantage, and Yahoo Finance (if required by `yfinance` in a specific context). Store these securely in Google Secret Manager.

### Local Development Setup

1.  **Clone the repository:**
    ```bash
    git clone [repository-url]
    cd multi-agent-financial-advisory-system
    ```

2.  **Install Dependencies for Each Service:**
    Navigate into each service directory (`budget_agent`, `financial_analysis_agent`, `orchestrator`) and install dependencies:
    ```bash
    cd budget_agent
    pip install -e .
    cd ../financial_analysis_agent
    pip install -e .
    cd ../orchestrator
    pip install -e .
    ```
    *(Note: The `pyproject.toml` specifies dependencies. Ensure `pip` is configured to use it, or create `requirements.txt` from it.)*

3.  **Environment Variables:**
    Create a `.env` file in the root of each service or set environment variables directly:
    *   `orchestrator/.env`:
        ```
        GEMINI_API_KEY="your_gemini_api_key"
        BUDGET_AGENT_URL="http://localhost:8001" # Or deployed URL
        FINANCIAL_ANALYSIS_AGENT_URL="http://localhost:8002" # Or deployed URL
        REDIS_HOST="localhost" # Or your Memorystore Redis host
        REDIS_PORT=6379 # Or your Memorystore Redis port
        REDIS_DB=0
        ```
    *   `budget_agent/.env`: (No specific API keys, uses `redis` if implemented for session or caching)
        ```
        REDIS_HOST="localhost"
        REDIS_PORT=6379
        REDIS_DB=0
        ```
    *   `financial_analysis_agent/.env`:
        ```
        ALPHA_VANTAGE_API_KEY="your_alpha_vantage_api_key"
        REDIS_HOST="localhost"
        REDIS_PORT=6379
        REDIS_DB=0
        ```

4.  **Run Redis Locally (for testing):**
    ```bash
    docker run --name some-redis -p 6379:6379 -d redis
    ```

5.  **Run Services Locally:**
    Open three separate terminal windows and run each service:
    *   **Budget Agent:**
        ```bash
        cd budget_agent
        uvicorn main:app --port 8001 --reload
        ```
    *   **Financial Analysis Agent:**
        ```bash
        cd financial_analysis_agent
        uvicorn main:app --port 8002 --reload
        ```
    *   **Orchestrator Agent:**
        ```bash
        cd orchestrator
        uvicorn main:app --port 8000 --reload
        ```

### Usage (Local)

Once all services are running, you can interact with the Orchestrator Agent (e.g., via `curl` or a tool like Postman/Insomnia):

```bash
# Example: Recognize intent and get a synthesized response
curl -X POST http://localhost:8000/orchestrate \
-H "Content-Type: application/json" \
-d '{"query": "What is the current price of TSLA?"}'

# Example: Get budget advice directly from the orchestrator (which calls the budget agent)
curl -X POST http://localhost:8000/orchestrate \
-H "Content-Type: application/json" \
-d '{"query": "Give me budget advice for a monthly income of $4000"}'
```

## ☁️ Deployment to Google Cloud Run

This section outlines the steps to deploy your services to Google Cloud Run. **Ensure you have completed the [Prerequisites](#prerequisites) for GCP setup.**

1.  **Authenticate `gcloud`:**
    ```bash
    gcloud auth login
    gcloud config set project your-gcp-project-id
    ```

2.  **Configure Docker for Google Container Registry (GCR):**
    ```bash
    gcloud auth configure-docker
    ```

3.  **Run Deployment Scripts:**
    Navigate to the `scripts` directory and execute each deployment script. Remember to update the `PROJECT_ID` and `REGION` variables within each script to match your GCP project and desired region.

    ```bash
    cd scripts
    chmod +x deploy_budget_agent.sh deploy_financial_analysis_agent.sh deploy_orchestrator.sh

    ./deploy_budget_agent.sh
    ./deploy_financial_analysis_agent.sh
    ./deploy_orchestrator.sh
    ```
    **Important**: After the initial deployment, you will need to update the `BUDGET_AGENT_URL` and `FINANCIAL_ANALYSIS_AGENT_URL` environment variables for the Orchestrator service to point to the actual URLs of your deployed Budget and Financial Analysis agents. You can find these URLs in the Cloud Run console or by using `gcloud run services describe`.

    You will also need to configure Secret Manager for each service during deployment (e.g., `GEMINI_API_KEY`, `ALPHA_VANTAGE_API_KEY`). This is typically done using the `--set-secrets` flag in the `gcloud run deploy` command, as indicated in the placeholder scripts.

## 🧪 Testing

### Unit Tests
Each service directory contains a `tests/` subdirectory with unit tests.
To run tests for a specific service:
```bash
cd <service-name> # e.g., budget_agent
pytest
```

### CI/CD Pipeline
A basic GitHub Actions CI pipeline (`.github/workflows/ci.yml`) is provided to lint, test, and build Docker images on push and pull request events.

## Contributing

(Guidelines for contributions will be added here.)

## License

(License information will be added here.)