from abc import ABC, abstractmethod
from typing import List, Optional, Union
from pydantic import BaseModel, Field

# Common Schemas for normalized output
class Quote(BaseModel):
    symbol: str
    price: float
    currency: Optional[str] = None
    market_cap: Optional[int] = None
    volume: Optional[int] = None
    previous_close: Optional[float] = None
    open: Optional[float] = None
    high: Optional[float] = None
    low: Optional[float] = None
    latest_trading_day: Optional[str] = None # From Alpha Vantage
    change: Optional[float] = None # From Alpha Vantage
    change_percent: Optional[str] = None # From Alpha Vantage

class HistoricalData(BaseModel):
    date: str
    open: float
    high: float
    low: float
    close: float
    volume: int

class DataProvider(ABC):
    """
    Abstract Base Class for financial data providers.
    Defines the common interface for fetching stock quotes and historical data,
    returning normalized Quote and HistoricalData objects.
    """

    @abstractmethod
    async def get_quote(self, symbol: str) -> Quote:
        """
        Fetches the current quote for a given stock symbol, returning a normalized Quote object.
        """
        pass

    @abstractmethod
    async def get_historical_data(self, symbol: str, period: str) -> List[HistoricalData]:
        """
        Fetches historical data for a given stock symbol and period, returning a list of normalized HistoricalData objects.
        """
        pass
