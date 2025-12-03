import httpx
from typing import Optional, Dict, Any, List
from financial_analysis_agent.clients.data_provider import DataProvider, Quote, HistoricalData

class AlphaVantageAPIError(Exception):
    """Custom exception for Alpha Vantage API errors."""
    pass

class AlphaVantageClient(DataProvider):
    def __init__(self, api_key: str, base_url: str = "https://www.alphavantage.co/query"):
        self.api_key = api_key
        self.base_url = base_url
        self.client = httpx.AsyncClient()

    async def _make_request(self, params: Dict[str, str]) -> Dict[str, Any]:
        params["apikey"] = self.api_key
        try:
            response = await self.client.get(self.base_url, params=params, timeout=5.0)
            response.raise_for_status()
            data = await response.json()
            if "Error Message" in data:
                raise AlphaVantageAPIError(data["Error Message"])
            if "Note" in data: # API rate limit message
                raise AlphaVantageAPIError(data["Note"])
            return data
        except httpx.HTTPStatusError as e:
            raise AlphaVantageAPIError(f"HTTP error occurred: {e.response.status_code} - {e.response.text}")
        except httpx.RequestError as e:
            raise AlphaVantageAPIError(f"Request error occurred: {e}")
        except Exception as e:
            raise AlphaVantageAPIError(f"An unexpected error occurred: {e}")

    async def get_quote(self, symbol: str) -> Quote:
        params = {
            "function": "GLOBAL_QUOTE",
            "symbol": symbol
        }
        data = await self._make_request(params)
        
        if "Global Quote" not in data or not data["Global Quote"]:
            raise AlphaVantageAPIError(f"No global quote data found for {symbol}")

        quote_data = data["Global Quote"]
        
        return Quote(
            symbol=quote_data.get("01. symbol", symbol),
            open=float(quote_data.get("02. open", 0)),
            high=float(quote_data.get("03. high", 0)),
            low=float(quote_data.get("04. low", 0)),
            price=float(quote_data.get("05. price", 0)),
            volume=int(quote_data.get("06. volume", 0)),
            latest_trading_day=quote_data.get("07. latest trading day"),
            previous_close=float(quote_data.get("08. previous close", 0)),
            change=float(quote_data.get("09. change", 0)),
            change_percent=quote_data.get("10. change percent"),
            currency="USD" # Alpha Vantage typically provides USD for stock quotes
        )

    async def get_historical_data(self, symbol: str, period: str = "compact") -> List[HistoricalData]:
        # Alpha Vantage's "period" is "outputsize": "compact" (100 days) or "full"
        # We will map "1mo", "3mo", etc. to "compact" for simplicity or require "compact"/"full"
        # For now, let's just use "compact"
        outputsize = "compact"
        if period == "full": # Allow passing "full" if needed
            outputsize = "full"

        params = {
            "function": "TIME_SERIES_DAILY",
            "symbol": symbol,
            "outputsize": outputsize
        }
        data = await self._make_request(params)

        if "Time Series (Daily)" not in data:
            raise AlphaVantageAPIError(f"No daily time series data found for {symbol}")
        
        time_series_data = data["Time Series (Daily)"]
        historical_data_list = []
        for date_str, daily_data in time_series_data.items():
            historical_data_list.append(
                HistoricalData(
                    date=date_str,
                    open=float(daily_data.get("1. open", 0)),
                    high=float(daily_data.get("2. high", 0)),
                    low=float(daily_data.get("3. low", 0)),
                    close=float(daily_data.get("4. close", 0)),
                    volume=int(daily_data.get("5. volume", 0)),
                )
            )
        
        return historical_data_list
