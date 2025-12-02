# Multi-Agent Financial Advisory System: Tasks

This document breaks down the development and deployment of the project into a series of manageable tasks.

## Phase 1: Project Setup & Core Infrastructure

- [ ] **Task 1.1: Initialize Git Repository:** Set up a new Git repository for the project.
- [ ] **Task 1.2: Set up GCP Project:** Create a new Google Cloud Project and enable required APIs (Cloud Run, Secret Manager, Memorystore, IAM).
- [ ] **Task 1.3: Initialize Python Project:**
    - Set up a monorepo structure with separate directories for each agent (`orchestrator`, `budget_agent`, `financial_analysis_agent`).
    - Initialize `pyproject.toml` with `uv` for package management.
    - Create initial `Dockerfile` for the services.
- [ ] **Task 1.4: Configure Secret Manager:** Create secrets for the Gemini API key and the Alpha Vantage API key.
- [ ] **Task 1.5: Provision Memorystore:** Create a Redis instance in Memorystore for session management.

## Phase 2: Agent & Tool Implementation

- [ ] **Task 2.1: Implement Budget Agent - 50/30/20 Tool:**
    - Create a FastAPI endpoint `/budget/calculate-50-30-20`.
    - Implement the logic to calculate needs, wants, and savings based on income.
- [ ] **Task 2.2: Implement Budget Agent - Spending Analysis Tool:**
    - Create a FastAPI endpoint `/budget/analyze-spending`.
    - Implement logic that takes a list of transactions/categories and provides simple insights.
- [ ] **Task 2.3: Implement Financial Analysis Agent - Stock Data Tool:**
    - Create a FastAPI endpoint `/financial/stock-data`.
    - Implement the integration with the Alpha Vantage API to fetch stock details.
- [ ] **Task 2.4: Implement Financial Analysis Agent - Portfolio Tool:**
    - Create a FastAPI endpoint `/financial/recommend-portfolio`.
    - Implement baseline logic to suggest a portfolio based on risk profile (e.g., using a predefined set of ETFs).
- [ ] **Task 2.5: Implement Financial Analysis Agent - Comparison Tool:**
    - Create a FastAPI endpoint `/financial/compare-stocks`.
    - Implement logic to fetch and present historical data for multiple stocks.

## Phase 3: Orchestrator and AI Logic

- [ ] **Task 3.1: Implement Orchestrator - Service Discovery:**
    - Implement a mechanism for the Orchestrator to know the internal addresses of the specialized agents.
- [ ] **Task 3.2: Implement Orchestrator - Intent Recognition:**
    - Write the core prompt for the Gemini API to perform intent recognition and entity extraction from the user query.
    - Implement the function that calls the Gemini API and parses its structured JSON output.
- [ ] **Task 3.3: Implement Orchestrator - Task Delegation Logic:**
    - Write the code that calls the appropriate specialized agent endpoints based on the recognized intents.
- [ ] **Task 3.4: Implement Orchestrator - Response Synthesis:**
    - Write the core prompt for the Gemini API to synthesize a final response from the data collected by the tools.
    - Implement the function that calls Gemini and returns the final answer.
- [ ] **Task 3.5: Implement Session Management:**
    - Integrate the Memorystore (Redis) client into the Orchestrator.
    - Implement functions to `get_session`, `save_session`, and `update_session`.

## Phase 4: Deployment & Integration

- [ ] **Task 4.1: Write CI/CD Pipeline:**
    - Create a GitHub Actions or Cloud Build pipeline.
    - The pipeline should build the Docker images for each agent and deploy them to Cloud Run.
    - The pipeline should handle secrets and environment variables for different environments (dev, prod).
- [ ] **Task 4.2: Deploy Initial Version:**
    - Manually run the deployment for the first time to ensure all services are running and communicating correctly.
- [ ] **Task 4.3: Implement Logging and Monitoring:**
    - Add structured logging (e.g., using `structlog`) to all services.
    - Set up a basic dashboard in Cloud Monitoring to track requests, latency, and errors for each Cloud Run service.

## Phase 5: Testing & Refinement

- [ ] **Task 5.1: Write Unit Tests:**
    - Add unit tests for all agent tools and critical logic paths.
- [ ] **Task 5.2: Write Integration Tests:**
    - Write tests for the Orchestrator to ensure it correctly calls the specialized agents and synthesizes responses.
    - Test the end-to-end flow with mock user queries.
- [ ] **Task 5.3: User Acceptance Testing (UAT):**
    - Manually test the system with the example queries from the requirements document to ensure it behaves as expected.
    - Refine prompts and logic based on UAT results.
