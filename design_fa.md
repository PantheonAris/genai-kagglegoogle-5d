# Multi-Agent Financial Advisory System: Design

This document outlines the high-level architecture and design of the Multi-Agent Financial Advisory System.

## 1. System Architecture

The system will be built on a serverless, microservices-oriented architecture using Google Cloud Platform (GCP) services. This design ensures scalability, modularity, and cost-effectiveness, aligning with the project's non-functional requirements.

Each core component (Orchestrator, Budget Agent, Financial Analysis Agent) will be deployed as an independent **Cloud Run** service. This allows each agent to be developed, deployed, and scaled independently.

### Architectural Diagram

```
+----------------+      +-------------------------+      +-----------------------+
|                |      |                         |      |                       |
|   User Client  |----->|   Orchestrator Agent    |<---->|   Session State       |
| (Web/Mobile App)|      |   (Cloud Run Service)   |      |   (Memorystore/      |
+----------------+      |                         |      |    Firestore)         |
                        +-----------+-------------+      +-----------------------+
                                    |
                                    | (Routes to appropriate agent)
                                    |
             +----------------------v----------------------+
             |                                              |
+------------+-------------+                  +-------------+--------------+
|                          |                  |                            |
|     Budget Agent         |                  |   Financial Analysis Agent |
| (Cloud Run Service)      |                  |   (Cloud Run Service)      |
|                          |                  |                            |
+--------------------------+                  +----------------------------+
| - 50/30/20 Tool          |                  | - Stock Data Tool (AlphaVantage) |
| - Spending Analysis Tool |                  | - Portfolio Recommender    |
| - Financial Calculator   |                  | - Stock Comparison Tool    |
+--------------------------+                  +----------------------------+

```

## 2. Component Design

### 2.1. Agents as Cloud Run Services

- **Orchestrator Agent:** The public-facing entry point of the system. It receives all user requests via an HTTP POST endpoint. Its primary role is to process natural language, determine intent, and delegate tasks to the specialized agents.
- **Budget Agent:** An internal Cloud Run service. It exposes endpoints for its specific tools (e.g., `/calculate-budget`, `/analyze-spending`).
- **Financial Analysis Agent:** An internal Cloud Run service. It exposes endpoints for its tools (e.g., `/get-stock-data`, `/recommend-portfolio`).

Communication between the Orchestrator and the specialized agents will be via synchronous, service-to-service REST API calls within the GCP network.

### 2.2. Technology Stack

- **Backend Framework:** Python with FastAPI. It's lightweight, fast, and well-suited for building API services on Cloud Run.
- **AI/LLM:** **Google Gemini Pro** via the Google AI Python SDK. Used by the Orchestrator for intent detection and response synthesis, and by specialized agents for interpreting nuanced requests.
- **Deployment:** **Google Cloud Run**. Provides serverless, scalable, and cost-effective container deployment.
- **Session State:** **Google Cloud Memorystore (Redis)**. Provides a low-latency, in-memory data store perfect for managing conversation state and session data. It is more performant for this use case than `InMemorySessionService` (which is not viable for a stateless, scaled service) or Firestore.
- **Secure Storage:** **Google Secret Manager** for storing API keys (e.g., for stock data APIs) and other secrets.
- **Stock Market Data:** A third-party API like **Alpha Vantage** will be used for real-time and historical stock data. The API key will be stored in Secret Manager.

## 3. Agent Interaction Flow

This flow illustrates how the system would handle a complex user query.

**User Query:** "I make $6000/month and want to start investing $500/month. Help me create a budget and suggest an investment portfolio."

1.  **Request to Orchestrator:** The user's client sends the query to the Orchestrator Agent's public endpoint.
2.  **State Loading:** The Orchestrator retrieves the user's session data from Memorystore using a session ID (e.g., from a JWT or an API key).
3.  **Intent Analysis (Gemini):** The Orchestrator sends a prompt to the Gemini API to analyze the user's query. The prompt will ask the model to identify the required tools/agents and extract key parameters.
    - **Gemini Output (structured JSON):**
      ```json
      {
        "intents": [
          {
            "agent": "BudgetAgent",
            "tool": "50/30/20",
            "parameters": { "income": 6000 }
          },
          {
            "agent": "FinancialAnalysisAgent",
            "tool": "recommend-portfolio",
            "parameters": { "investment_amount": 500, "risk_profile": "moderate" }
          }
        ]
      }
      ```
4.  **Task Delegation:** The Orchestrator iterates through the identified intents:
    - It makes a service-to-service call to the **Budget Agent** (`/calculate-budget`) with the income parameter.
    - It makes a service-to-service call to the **Financial Analysis Agent** (`/recommend-portfolio`) with the investment amount. A default risk profile may be assumed or a clarifying question asked in a subsequent turn.
5.  **Agent Execution:**
    - The Budget Agent calculates the 50/30/20 budget and returns a structured JSON response.
    - The Financial Analysis Agent determines a suitable "moderate risk" portfolio and returns a structured JSON response.
6.  **Response Synthesis (Gemini):** The Orchestrator gathers the JSON responses from the specialized agents. It then sends a final prompt to the Gemini API, providing both the original user query and the collected data from the tools.
    - **Prompt to Gemini:** "The user asked: '...'. The budget tool returned: `{...}`. The portfolio tool returned: `{...}`. Synthesize these into a friendly, comprehensive answer."
7.  **Final Response to User:** The Gemini API generates a natural language response, which the Orchestrator forwards to the user.
8.  **State Update:** The Orchestrator updates the session state in Memorystore with the new turn of conversation.

## 4. Cost Optimization Design

- **Scale to Zero:** Cloud Run automatically scales down to zero instances when there is no traffic, eliminating costs for idle time.
- **Memorystore Instance Sizing:** Start with the smallest possible Memorystore for Redis instance and monitor usage.
- **Caching:** Implement a caching layer for the Financial Analysis Agent. Stock data for popular tickers can be cached for short periods (e.g., 1-5 minutes) in Memorystore to reduce the number of calls to the external (and potentially costly) stock data API.
- **Efficient Gemini Prompts:** Design prompts to be concise and clear to minimize token usage for both requests and responses. Use structured inputs and outputs where possible.
