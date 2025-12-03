import httpx
from typing import Dict, Any

class ServiceClient:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.client = httpx.AsyncClient()

    async def post(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Makes a POST request to a specified endpoint on the service.
        """
        try:
            response = await self.client.post(f"{self.base_url}{endpoint}", json=data, timeout=10.0)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            # You might want to log the error details here
            raise Exception(f"HTTP error occurred: {e.response.status_code} - {e.response.text}")
        except httpx.RequestError as e:
            # You might want to log the error details here
            raise Exception(f"Request error occurred: {e}")

class AgentClients:
    def __init__(self, budget_agent_url: str, financial_analysis_agent_url: str):
        self.budget = ServiceClient(base_url=budget_agent_url)
        self.financial_analysis = ServiceClient(base_url=financial_analysis_agent_url)

# In a real application, these URLs would come from a configuration service or environment variables.
# For example:
# BUDGET_AGENT_URL = os.getenv("BUDGET_AGENT_URL", "http://localhost:8001")
# FINANCIAL_ANALYSIS_AGENT_URL = os.getenv("FINANCIAL_ANALYSIS_AGENT_URL", "http://localhost:8002")

# agent_clients = AgentClients(
#     budget_agent_url=BUDGET_AGENT_URL,
#     financial_analysis_agent_url=FINANCIAL_ANALYSIS_AGENT_URL
# )
