# Multi-Agent Financial Advisory System: Design (v2)

This document outlines the high-level architecture and design of the Multi-Agent Financial Advisory System.

## 1. System Architecture

The system will be built on a serverless, microservices-oriented architecture using Google Cloud Platform (GCP) services. This design ensures scalability, modularity, and cost-effectiveness, aligning with the project's non-functional requirements.

Each core component (Orchestrator, Budget Agent, Financial Analysis Agent) will be deployed as an independent **Cloud Run** service. This allows each agent to be developed, deployed, and scaled independently.

### Architectural Diagram

```
+----------------+      +-------------------------+      +-----------------------+
|                |      |                         |      |                       |
|   User Client  |----->|   Orchestrator Agent    |<---->|   Session State       |
| (Web/Mobile App)|      |   (Cloud Run Service)   |      |   (Memorystore)       |
+----------------+      |                         |      +-----------------------+
                        +-----------+-------------+
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
| - 50/30/20 Tool          |                  | - Stock Data Tool          |
| - Spending Analysis Tool |                  |   - Abstraction Layer      |
| - Financial Calculator   |                  |     - Alpha Vantage Client |
+--------------------------+                  |     - Yahoo Finance Client |
                                              | - Portfolio Recommender    |
                                              | - Stock Comparison Tool    |
                                              +----------------------------+
```

## 2. Component Design

### 2.1. Agents as Cloud Run Services

- **Orchestrator Agent:** The public-facing entry point of the system. It receives all user requests via an HTTP POST endpoint. Its primary role is to process natural language, determine intent, and delegate tasks to the specialized agents.
- **Budget Agent:** An internal Cloud Run service. It exposes endpoints for its specific tools (e.g., `/calculate-budget`, `/analyze-spending`).
- **Financial Analysis Agent:** An internal Cloud Run service. It exposes endpoints for its tools. A key feature of this agent is a **Data Source Abstraction Layer** to handle multiple financial data providers.

Communication between the Orchestrator and the specialized agents will be via synchronous, service-to-service REST API calls within the GCP network.

### 2.2. Technology Stack

- **Backend Framework:** Python with FastAPI.
- **AI/LLM:** **Google Gemini Pro** via the Google AI Python SDK.
- **Deployment:** **Google Cloud Run**.
- **Session State:** **Google Cloud Memorystore (Redis)**.
- **Secure Storage:** **Google Secret Manager** for all API keys.
- **Stock Market Data:**
    - The system will use multiple third-party APIs for redundancy and broad data coverage.
    - **Primary:** **Alpha Vantage**.
    - **Secondary:** **Yahoo Finance API** (via a library like `yfinance`).
    - API keys for all providers will be stored in Secret Manager.

### 2.3. Financial Data Abstraction Layer

To seamlessly handle multiple data providers, the Financial Analysis Agent will implement an abstraction layer.

- **`DataProvider` Interface:** A simple, standardized interface will be defined with methods like `get_stock_quote(ticker)` and `get_historical_data(ticker, period)`.
- **Concrete Implementations:**
    - `AlphaVantageClient`: Implements the `DataProvider` interface, fetching data from Alpha Vantage.
    - `YahooFinanceClient`: Implements the `DataProvider` interface, fetching data from Yahoo Finance.
- **Fallback and Selection Logic:** The Stock Data Tool will first try the primary provider (Alpha Vantage). If the request fails or times out, it will automatically fall back to the secondary provider (Yahoo Finance). This ensures high availability for market data.

## 3. Agent Interaction Flow

The overall agent interaction flow remains the same. The key difference is within the `Financial Analysis Agent`. When it receives a request for stock data, it will use its internal data abstraction layer to fetch the information, transparent to the Orchestrator.

1.  **Request to Orchestrator** -> **Intent Analysis** -> **Task Delegation**.
2.  Orchestrator calls the Financial Analysis Agent's `/financial/stock-data` endpoint.
3.  **Inside Financial Analysis Agent:**
    a. The endpoint calls the `DataProvider.get_stock_quote("TICKER")` method from the abstraction layer.
    b. The abstraction layer first attempts to call `AlphaVantageClient.get_stock_quote()`.
    c. If the Alpha Vantage call fails, the layer catches the exception and calls `YahooFinanceClient.get_stock_quote()` as a fallback.
    d. The fetched data is returned to the endpoint in a standardized format.
4.  The agent returns the standardized data to the Orchestrator.
5.  **Response Synthesis** -> **Final Response to User**.

## 4. Cost Optimization Design

- **Scale to Zero:** Cloud Run is used for all services.
- **Memorystore Instance Sizing:** Start with a minimal Redis instance.
- **Intelligent Caching:** The caching layer in Memorystore will store data using a provider-agnostic key (e.g., `stock:tsla`). This means a cache fill from Alpha Vantage can serve a subsequent request that might have otherwise gone to Yahoo Finance, reducing overall API calls.
- **Efficient Gemini Prompts:** Prompts remain concise to minimize token usage.
- **Cost-Effective Data Source:** The abstraction layer can be extended with logic to choose the cheapest API for a given request type, if cost structures differ significantly.
