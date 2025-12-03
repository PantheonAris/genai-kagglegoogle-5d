from typing import Dict, Type
from financial_analysis_agent.clients.data_provider import DataProvider
from financial_analysis_agent.clients.alpha_vantage import AlphaVantageClient
from financial_analysis_agent.clients.yahoo_finance import YahooFinanceClient

class DataProviderFactory:
    """
    A factory class to provide instances of various financial data providers.
    """
    def __init__(self, api_keys: Dict[str, str]):
        self._providers: Dict[str, DataProvider] = {}
        
        # Initialize AlphaVantageClient if API key is provided
        if "ALPHA_VANTAGE_API_KEY" in api_keys and api_keys["ALPHA_VANTAGE_API_KEY"]:
            self._providers["alpha_vantage"] = AlphaVantageClient(api_keys["ALPHA_VANTAGE_API_KEY"])
        
        # Initialize YahooFinanceClient (no API key needed directly for yfinance library)
        self._providers["yahoo_finance"] = YahooFinanceClient()

        if not self._providers:
            raise ValueError("No data providers could be initialized. Check API keys and configuration.")

    def get_provider(self, provider_name: str) -> DataProvider:
        """
        Retrieves a data provider instance by name.
        """
        if provider_name not in self._providers:
            raise ValueError(f"Data provider '{provider_name}' not found.")
        return self._providers[provider_name]

    def get_all_providers(self) -> Dict[str, DataProvider]:
        """
        Returns all initialized data providers.
        """
        return self._providers
