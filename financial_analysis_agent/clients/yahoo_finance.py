import yfinance as yf
from typing import Optional, Dict, Any, List
from datetime import datetime
import pandas as pd # yfinance returns pandas DataFrames

from financial_analysis_agent.clients.data_provider import DataProvider, Quote, HistoricalData

class YahooFinanceAPIError(Exception):
    """Custom exception for Yahoo Finance API errors."""
    pass

class YahooFinanceClient(DataProvider):
    def __init__(self):
        # yfinance does not require an API key directly.
        # It scrapes data, so rate limits or IP bans can occur.
        pass

    async def get_quote(self, symbol: str) -> Quote:
        ticker = yf.Ticker(symbol)
        try:
            # yfinance.Ticker().info can be slow; needs to be awaited or run in a threadpool
            # For now, we'll assume it's "fast enough" or that the abstraction layer handles concurrency
            # Actual implementation would use run_in_threadpool if a sync library
            info = ticker.info
            
            if not info or info.get('regularMarketPrice') is None:
                raise YahooFinanceAPIError(f"Could not retrieve quote for {symbol}. Data not found or invalid symbol.")

            return Quote(
                symbol=info.get('symbol', symbol),
                price=info.get('regularMarketPrice'),
                currency=info.get('currency'),
                market_cap=info.get('marketCap'),
                volume=info.get('regularMarketVolume'),
                previous_close=info.get('previousClose'),
                open=info.get('regularMarketOpen'),
                high=info.get('regularMarketDayHigh'),
                low=info.get('regularMarketDayLow'),
                # Alpha Vantage specific fields, not always available in yfinance
                latest_trading_day=None,
                change=None,
                change_percent=None,
            )
        except Exception as e:
            # yfinance can raise various exceptions (e.g., KeyError if symbol not found, ValueError)
            # We catch them and re-raise as our custom API error
            raise YahooFinanceAPIError(f"Error fetching quote for {symbol}: {e}")

    async def get_historical_data(self, symbol: str, period: str = "1mo") -> List[HistoricalData]:
        # periods: 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max
        ticker = yf.Ticker(symbol)
        try:
            hist: pd.DataFrame = ticker.history(period=period)
            if hist.empty:
                raise YahooFinanceAPIError(f"No historical data found for {symbol} for period {period}.")
            
            historical_data_list = []
            for index, row in hist.iterrows():
                historical_data_list.append(
                    HistoricalData(
                        date=index.strftime('%Y-%m-%d'), # Format date to string
                        open=row['Open'],
                        high=row['High'],
                        low=row['Low'],
                        close=row['Close'],
                        volume=row['Volume']
                    )
                )
            return historical_data_list
        except Exception as e:
            raise YahooFinanceAPIError(f"Error fetching historical data for {symbol} (period={period}): {e}")
