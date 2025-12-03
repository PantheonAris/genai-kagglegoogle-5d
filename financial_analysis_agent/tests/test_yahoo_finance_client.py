import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from financial_analysis_agent.clients.yahoo_finance import YahooFinanceClient, YahooFinanceAPIError
from financial_analysis_agent.clients.data_provider import Quote, HistoricalData
import pandas as pd
from datetime import datetime
import re # Import the re module

# Mock API Key (not used by yfinance directly, but kept for consistency if it were needed)
TEST_API_KEY = "test_api_key"

@pytest.fixture
def yahoo_finance_client():
    """Fixture to provide a YahooFinanceClient instance."""
    return YahooFinanceClient()

@pytest.mark.asyncio
async def test_get_quote_success(yahoo_finance_client):
    mock_info = {
        'symbol': 'AAPL',
        'regularMarketPrice': 170.0,
        'currency': 'USD',
        'marketCap': 2800000000000,
        'regularMarketVolume': 100000000,
        'previousClose': 169.0,
        'regularMarketOpen': 169.5,
        'regularMarketDayHigh': 170.5,
        'regularMarketDayLow': 169.0,
    }
    with patch('yfinance.Ticker', autospec=True) as mock_ticker_class:
        mock_ticker_instance = mock_ticker_class.return_value
        mock_ticker_instance.info = mock_info
        
        quote = await yahoo_finance_client.get_quote("AAPL")

        assert isinstance(quote, Quote)
        assert quote.symbol == "AAPL"
        assert quote.price == 170.0
        assert quote.market_cap == 2800000000000
        mock_ticker_class.assert_called_once_with("AAPL")

@pytest.mark.asyncio
async def test_get_quote_invalid_symbol(yahoo_finance_client):
    mock_info = {} # Empty info for invalid symbol
    with patch('yfinance.Ticker', autospec=True) as mock_ticker_class:
        mock_ticker_instance = mock_ticker_class.return_value
        mock_ticker_instance.info = mock_info

        with pytest.raises(YahooFinanceAPIError, match=re.escape("Could not retrieve quote for INVALID. Data not found or invalid symbol.")):
            await yahoo_finance_client.get_quote("INVALID")
        mock_ticker_class.assert_called_once_with("INVALID")

@pytest.mark.asyncio
async def test_get_quote_missing_price(yahoo_finance_client):
    mock_info = {
        'symbol': 'AAPL',
        'currency': 'USD',
        'marketCap': 2800000000000,
    } # Missing 'regularMarketPrice'
    with patch('yfinance.Ticker', autospec=True) as mock_ticker_class:
        mock_ticker_instance = mock_ticker_class.return_value
        mock_ticker_instance.info = mock_info

        with pytest.raises(YahooFinanceAPIError, match=re.escape("Could not retrieve quote for AAPL. Data not found or invalid symbol.")):
            await yahoo_finance_client.get_quote("AAPL")
        mock_ticker_class.assert_called_once_with("AAPL")

@pytest.mark.asyncio
async def test_get_historical_data_success(yahoo_finance_client):
    mock_hist_data = pd.DataFrame({
        'Open': [160.0, 161.0],
        'High': [162.0, 163.0],
        'Low': [159.0, 160.0],
        'Close': [161.0, 162.0],
        'Volume': [50000000, 60000000]
    }, index=pd.to_datetime(['2023-11-20', '2023-11-21']))

    with patch('yfinance.Ticker', autospec=True) as mock_ticker_class:
        mock_ticker_instance = mock_ticker_class.return_value
        mock_ticker_instance.history.return_value = mock_hist_data
        
        historical_data = await yahoo_finance_client.get_historical_data("AAPL", period="2d")

        assert isinstance(historical_data, list)
        assert len(historical_data) == 2
        assert all(isinstance(data, HistoricalData) for data in historical_data)
        assert historical_data[0].date == "2023-11-20"
        assert historical_data[0].close == 161.0
        assert historical_data[1].date == "2023-11-21"
        assert historical_data[1].volume == 60000000
        mock_ticker_class.assert_called_once_with("AAPL")
        mock_ticker_instance.history.assert_called_once_with(period="2d")

@pytest.mark.asyncio
async def test_get_historical_data_no_data(yahoo_finance_client):
    mock_hist_data = pd.DataFrame() # Empty DataFrame for no data
    with patch('yfinance.Ticker', autospec=True) as mock_ticker_class:
        mock_ticker_instance = mock_ticker_class.return_value
        mock_ticker_instance.history.return_value = mock_hist_data

        with pytest.raises(YahooFinanceAPIError, match=re.escape("No historical data found for AAPL for period 1d.")):
            await yahoo_finance_client.get_historical_data("AAPL", period="1d")
        mock_ticker_class.assert_called_once_with("AAPL")
        mock_ticker_instance.history.assert_called_once_with(period="1d")

@pytest.mark.asyncio
async def test_get_historical_data_exception(yahoo_finance_client):
    with patch('yfinance.Ticker', autospec=True) as mock_ticker_class:
        mock_ticker_instance = mock_ticker_class.return_value
        mock_ticker_instance.history.side_effect = Exception("Network error")

        with pytest.raises(YahooFinanceAPIError, match=re.escape("Error fetching historical data for GOOG (period=1mo): Network error")):
            await yahoo_finance_client.get_historical_data("GOOG", period="1mo")
        mock_ticker_class.assert_called_once_with("GOOG")
        mock_ticker_instance.history.assert_called_once_with(period="1mo")
