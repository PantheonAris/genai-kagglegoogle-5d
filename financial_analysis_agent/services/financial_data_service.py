from typing import Dict, List, Optional
from financial_analysis_agent.clients.data_provider import DataProvider, Quote, HistoricalData
from financial_analysis_agent.clients.data_provider_factory import DataProviderFactory
from financial_analysis_agent.clients.alpha_vantage import AlphaVantageAPIError
from financial_analysis_agent.clients.yahoo_finance import YahooFinanceAPIError
from financial_analysis_agent.utils.cache import CacheManager
from financial_analysis_agent.schemas import StockPerformance
import redis.asyncio as redis # For type hinting the Redis client
import asyncio

class FinancialDataServiceError(Exception):
    """Custom exception for FinancialDataService errors."""
    pass

class FinancialDataService:
    def __init__(self, provider_factory: DataProviderFactory, redis_client: redis.Redis):
        self._providers = provider_factory.get_all_providers()
        
        # Define preferred order of providers for fallback
        self._provider_order = ["alpha_vantage", "yahoo_finance"] # Prioritize Alpha Vantage
        self._active_providers: List[str] = [p for p in self._provider_order if p in self._providers]

        if not self._active_providers:
            raise FinancialDataServiceError("No active data providers available.")

        self.cache_manager = CacheManager(redis_client=redis_client)

        # Apply caching decorators dynamically after cache_manager is initialized
        self.get_quote = self.cache_manager.cache(key_prefix="financial_data:quote", ttl=300)(self._get_quote_uncached)
        self.get_historical_data = self.cache_manager.cache(key_prefix="financial_data:historical", ttl=3600)(self._get_historical_data_uncached)

    async def _get_quote_uncached(self, symbol: str) -> Quote:
        """
        Fetches a stock quote with fallback logic (uncached version).
        Tries providers in order until one succeeds.
        """
        errors = []
        for provider_name in self._active_providers:
            provider = self._providers[provider_name]
            try:
                quote = await provider.get_quote(symbol)
                return quote
            except (AlphaVantageAPIError, YahooFinanceAPIError) as e:
                errors.append(f"Provider {provider_name} failed for {symbol}: {e}")
            except Exception as e:
                errors.append(f"Provider {provider_name} encountered an unexpected error for {symbol}: {e}")
        
        raise FinancialDataServiceError(f"Failed to fetch quote for {symbol} after trying all providers. Errors: {'; '.join(errors)}")

    async def _get_historical_data_uncached(self, symbol: str, period: str) -> List[HistoricalData]:
        """
        Fetches historical data with fallback logic (uncached version).
        Tries providers in order until one succeeds.
        """
        errors = []
        for provider_name in self._active_providers:
            provider = self._providers[provider_name]
            try:
                historical_data = await provider.get_historical_data(symbol, period)
                if historical_data: # Ensure data is not empty
                    return historical_data
                else:
                    errors.append(f"Provider {provider_name} returned empty historical data for {symbol}, period {period}")
            except (AlphaVantageAPIError, YahooFinanceAPIError) as e:
                errors.append(f"Provider {provider_name} failed for {symbol}, period {period}: {e}")
            except Exception as e:
                errors.append(f"Provider {provider_name} encountered an unexpected error for {symbol}, period {period}: {e}")
        
        raise FinancialDataServiceError(f"Failed to fetch historical data for {symbol}, period {period} after trying all providers. Errors: {'; '.join(errors)}")

    async def compare_stocks(self, symbols: List[str], period: str) -> List[StockPerformance]:
        """
        Compares the performance of multiple stocks over a given period.
        """
        async def get_performance(symbol: str):
            try:
                hist_data = await self.get_historical_data(symbol, period)
                if not hist_data or len(hist_data) < 2:
                    return None
                
                # Assuming data is sorted with the most recent date first
                start_price = hist_data[-1].close
                end_price = hist_data[0].close
                change = end_price - start_price
                change_percent = (change / start_price) * 100 if start_price != 0 else 0

                return StockPerformance(
                    symbol=symbol,
                    start_price=start_price,
                    end_price=end_price,
                    change=change,
                    change_percent=change_percent,
                )
            except FinancialDataServiceError as e:
                # Log or handle error for a single symbol
                print(f"Could not fetch data for {symbol}: {e}")
                return None

        tasks = [get_performance(symbol) for symbol in symbols]
        results = await asyncio.gather(*tasks)
        
        # Filter out None results where data fetching failed
        performance_comparison = [res for res in results if res is not None]
        
        if not performance_comparison:
            raise FinancialDataServiceError("Could not retrieve performance data for any of the specified symbols.")
            
        return performance_comparison
