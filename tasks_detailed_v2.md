# Multi-Agent Financial Advisory System: Detailed Tasks (v2)

This document provides a detailed breakdown of the development and deployment tasks for the project.

## Phase 1: Project Setup & Core Infrastructure (Estimate: 1-2 Days)

- [ ] **Task 1.1: Version Control Setup**
    - [ ] 1.1.1: Initialize a new Git repository.
    - [ ] 1.1.2: Create a `.gitignore` file.
    - [ ] 1.1.3: Create a `README.md`.
- [ ] **Task 1.2: Google Cloud Project Configuration**
    - [ ] 1.2.1: Create a new GCP Project and link billing.
    - [ ] 1.2.2: Enable APIs: Cloud Run, Secret Manager, Memorystore, IAM, Cloud Build, Artifact Registry.
    - [ ] 1.2.3: Create a dedicated service account with least-privilege IAM roles.
- [ ] **Task 1.3: Monorepo & Application Scaffolding**
    - [ ] 1.3.1: Create service directories: `orchestrator`, `budget_agent`, `financial_analysis_agent`.
    - [ ] 1.3.2: Initialize `pyproject.toml` in each service with base dependencies.
    - [ ] 1.3.3: Create skeleton `main.py` in each service with a `/health` endpoint.
    - [ ] 1.3.4: Create multi-stage `Dockerfile` for each service.
- [ ] **Task 1.4: Secrets Management**
    - [ ] 1.4.1: Create secrets in Secret Manager for `GEMINI_API_KEY`, `ALPHA_VANTAGE_API_KEY`, and `YAHOO_FINANCE_API_KEY` (if required).
    - [ ] 1.4.2: Grant the service account access to these secrets.
- [ ] **Task 1.5: Session State Infrastructure**
    - [ ] 1.5.1: Provision a Memorystore for Redis instance.

## Phase 2: Agent & Tool Implementation (Estimate: 6-8 Days)

- [ ] **Task 2.1: Implement Budget Agent Tools**
    - [ ] 2.1.1: Implement and test the 50/30/20 Budget Tool.
    - [ ] 2.1.2: Implement and test the Spending Analysis Tool.
- [ ] **Task 2.2: Implement Financial Data Source Clients**
    - [ ] **Task 2.2.1: Alpha Vantage Client**
        - [ ] 2.2.1.1: Add `httpx` to Financial Analysis Agent dependencies.
        - [ ] 2.2.1.2: Create a client module to call the Alpha Vantage API.
        - [ ] 2.2.1.3: Implement functions for stock quotes and historical data.
        - [ ] 2.2.1.4: Write unit tests mocking the external API.
    - [ ] **Task 2.2.2: Yahoo Finance Client**
        - [ ] 2.2.2.1: Add `yfinance` to Financial Analysis Agent dependencies.
        - [ ] 2.2.2.2: Create a client module to call the Yahoo Finance API.
        - [ ] 2.2.2.3: Implement functions for stock quotes and historical data.
        - [ ] 2.2.2.4: Write unit tests mocking the library's calls.
- [ ] **Task 2.3: Implement Financial Data Abstraction Layer**
    - [ ] 2.3.1: Define a `DataProvider` abstract base class (or Protocol) with common methods (`get_stock_quote`, etc.).
    - [ ] 2.3.2: Refactor the Alpha Vantage and Yahoo Finance clients to implement the `DataProvider` interface.
    - [ ] 2.3.3: Create a `DataProviderFactory` or manager that holds instances of the clients.
    - [ ] 2.3.4: Implement fallback logic in the manager (e.g., `try provider1, on error, try provider2`).
    - [ ] 2.3.5: Implement a caching decorator or logic within the manager to cache results in Redis.
- [ ] **Task 2.4: Implement Financial Analysis Agent Endpoints**
    - [ ] 2.4.1: Implement `/financial/stock-data` endpoint, which uses the data abstraction layer.
    - [ ] 2.4.2: Implement `/financial/recommend-portfolio` endpoint.
    - [ ] 2.4.3: Implement `/financial/compare-stocks` endpoint, using the data abstraction layer.

## Phase 3: Orchestrator and AI Logic (Estimate: 4-6 Days)

- [ ] **Task 3.1: Orchestrator - Service Communication & Session**
    - [ ] 3.1.1: Implement an `httpx` client for internal service-to-service calls.
    - [ ] 3.1.2: Implement Redis-based session management (`get_session`, `save_session`).
- [ ] **Task 3.2: Orchestrator - Intent Recognition (Gemini)**
    - [ ] 3.2.1: Draft v1 of the intent recognition prompt with few-shot examples.
    - [ ] 3.2.2: Implement the Gemini API call and Pydantic-based JSON parsing and validation.
- [ ] **Task 3.3: Orchestrator - Task Delegation & Synthesis**
    - [ ] 3.3.1: Implement the logic to loop through recognized intents and call agent tools.
    - [ ] 3.3.2: Draft v1 of the response synthesis prompt.
    - [ ] 3.3.3: Implement the final Gemini call to generate the user-facing response.

## Phase 4: Deployment & Integration (Estimate: 3-4 Days)

- [ ] **Task 4.1: CI/CD Pipeline (Cloud Build or GitHub Actions)**
    - [ ] 4.1.1: Create pipeline with stages for lint, test, build, and deploy.
    - [ ] 4.1.2: Configure triggers (e.g., on push to `main`).
- [ ] **Task 4.2: Initial Deployment & Configuration**
    - [ ] 4.2.1: Write `gcloud` deployment scripts for all services.
    - [ ] 4.2.2: Set up Cloud Run services with correct IAM, ingress settings, and secret mappings.
- [ ] **Task 4.3: Logging & Monitoring**
    - [ ] 4.3.1: Integrate structured logging in all services.
    - [ ] 4.3.2: Create a Cloud Monitoring dashboard with key service-level indicators (SLIs).

## Phase 5: Testing & Refinement (Estimate: 3-5 Days)

- [ ] **Task 5.1: Comprehensive Testing**
    - [ ] 5.1.1: Achieve >80% unit test coverage.
    - [ ] 5.1.2: Write end-to-end integration tests for primary user flows.
- [ ] **Task 5.2: User Acceptance Testing (UAT) & Prompt Tuning**
    - [ ] 5.2.1: Manually test with a diverse set of queries.
    - [ ] 5.2.2: Iteratively refine and version the Gemini prompts based on test results to improve accuracy and tone.
    - [ ] 5.2.3: Add failing UAT cases to the permanent integration test suite.
