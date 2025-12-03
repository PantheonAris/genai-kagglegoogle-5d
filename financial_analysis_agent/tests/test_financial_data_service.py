import pytest
from unittest.mock import AsyncMock, MagicMock
from financial_analysis_agent.services.financial_data_service import FinancialDataService, FinancialDataServiceError
from financial_analysis_agent.clients.data_provider import Quote, HistoricalData, DataProvider
from financial_analysis_agent.clients.data_provider_factory import DataProviderFactory
from financial_analysis_agent.clients.alpha_vantage import AlphaVantageAPIError
from financial_analysis_agent.clients.yahoo_finance import YahooFinanceAPIError
import json

@pytest.fixture
def mock_alpha_vantage_client():
    mock = AsyncMock(spec=DataProvider)
    mock.get_quote.return_value = Quote(symbol="IBM", price=150.0)
    mock.get_historical_data.return_value = [HistoricalData(date="2023-01-01", open=100.0, high=105.0, low=99.0, close=103.0, volume=1000000)]
    return mock

@pytest.fixture
def mock_yahoo_finance_client():
    mock = AsyncMock(spec=DataProvider)
    mock.get_quote.return_value = Quote(symbol="IBM", price=150.5, currency="USD")
    mock.get_historical_data.return_value = [HistoricalData(date="2023-01-01", open=100.0, high=105.0, low=99.0, close=103.0, volume=1000000)]
    return mock

@pytest.fixture
def mock_provider_factory(mock_alpha_vantage_client, mock_yahoo_finance_client):
    factory = MagicMock(spec=DataProviderFactory)
    factory.get_all_providers.return_value = {
        "alpha_vantage": mock_alpha_vantage_client,
        "yahoo_finance": mock_yahoo_finance_client
    }
    return factory

@pytest.fixture
def mock_redis_client():
    mock = AsyncMock()
    mock.get.return_value = None # By default, cache is empty
    mock.setex.return_value = None
    return mock

@pytest.mark.asyncio
async def test_get_quote_primary_succeeds(mock_provider_factory, mock_alpha_vantage_client, mock_yahoo_finance_client, mock_redis_client):
    service = FinancialDataService(mock_provider_factory, mock_redis_client)
    quote = await service.get_quote("IBM")
    mock_alpha_vantage_client.get_quote.assert_awaited_once_with("IBM")
    mock_yahoo_finance_client.get_quote.assert_not_awaited()
    assert quote.symbol == "IBM"
    assert quote.price == 150.0
    mock_redis_client.get.assert_awaited_once() # Check cache read
    mock_redis_client.setex.assert_awaited_once() # Check cache write

@pytest.mark.asyncio
async def test_get_quote_primary_fails_fallback_succeeds(mock_provider_factory, mock_alpha_vantage_client, mock_yahoo_finance_client, mock_redis_client):
    mock_alpha_vantage_client.get_quote.side_effect = AlphaVantageAPIError("API down")
    service = FinancialDataService(mock_provider_factory, mock_redis_client)
    quote = await service.get_quote("IBM")
    mock_alpha_vantage_client.get_quote.assert_awaited_once_with("IBM")
    mock_yahoo_finance_client.get_quote.assert_awaited_once_with("IBM")
    assert quote.symbol == "IBM"
    assert quote.price == 150.5 # Should get from Yahoo Finance
    mock_redis_client.get.assert_awaited_once() # Check cache read
    mock_redis_client.setex.assert_awaited_once() # Check cache write

@pytest.mark.asyncio
async def test_get_quote_all_fail(mock_provider_factory, mock_alpha_vantage_client, mock_yahoo_finance_client, mock_redis_client):
    mock_alpha_vantage_client.get_quote.side_effect = AlphaVantageAPIError("API down")
    mock_yahoo_finance_client.get_quote.side_effect = YahooFinanceAPIError("Rate limited")
    service = FinancialDataService(mock_provider_factory, mock_redis_client)
    with pytest.raises(FinancialDataServiceError, match="Failed to fetch quote for IBM after trying all providers"):
        await service.get_quote("IBM")
    mock_alpha_vantage_client.get_quote.assert_awaited_once_with("IBM")
    mock_yahoo_finance_client.get_quote.assert_awaited_once_with("IBM")
    mock_redis_client.get.assert_awaited_once() # Check cache read
    mock_redis_client.setex.assert_not_awaited() # No cache write on failure

@pytest.mark.asyncio
async def test_get_quote_from_cache(mock_provider_factory, mock_alpha_vantage_client, mock_redis_client):
    cached_quote = Quote(symbol="GOOG", price=100.0)
    mock_redis_client.get.return_value = cached_quote.json() # Simulate cached data
    service = FinancialDataService(mock_provider_factory, mock_redis_client)
    quote = await service.get_quote("GOOG")

    mock_redis_client.get.assert_awaited_once()
    mock_alpha_vantage_client.get_quote.assert_not_awaited() # Provider should not be called
    mock_redis_client.setex.assert_not_awaited() # No cache write if read from cache

    assert quote.symbol == "GOOG"
    assert quote.price == 100.0

@pytest.mark.asyncio
async def test_get_historical_data_primary_succeeds(mock_provider_factory, mock_alpha_vantage_client, mock_yahoo_finance_client, mock_redis_client):
    service = FinancialDataService(mock_provider_factory, mock_redis_client)
    hist_data = await service.get_historical_data("IBM", "1mo")
    mock_alpha_vantage_client.get_historical_data.assert_awaited_once_with("IBM", "1mo")
    mock_yahoo_finance_client.get_historical_data.assert_not_awaited()
    assert len(hist_data) == 1
    assert hist_data[0].date == "2023-01-01"
    mock_redis_client.get.assert_awaited_once()
    mock_redis_client.setex.assert_awaited_once()

@pytest.mark.asyncio
async def test_get_historical_data_primary_fails_fallback_succeeds(mock_provider_factory, mock_alpha_vantage_client, mock_yahoo_finance_client, mock_redis_client):
    mock_alpha_vantage_client.get_historical_data.side_effect = AlphaVantageAPIError("API down")
    service = FinancialDataService(mock_provider_factory, mock_redis_client)
    hist_data = await service.get_historical_data("IBM", "1mo")
    mock_alpha_vantage_client.get_historical_data.assert_awaited_once_with("IBM", "1mo")
    mock_yahoo_finance_client.get_historical_data.assert_awaited_once_with("IBM", "1mo")
    assert len(hist_data) == 1
    assert hist_data[0].date == "2023-01-01"
    mock_redis_client.get.assert_awaited_once()
    mock_redis_client.setex.assert_awaited_once()

@pytest.mark.asyncio
async def test_get_historical_data_all_fail(mock_provider_factory, mock_alpha_vantage_client, mock_yahoo_finance_client, mock_redis_client):
    mock_alpha_vantage_client.get_historical_data.side_effect = AlphaVantageAPIError("API down")
    mock_yahoo_finance_client.get_historical_data.side_effect = YahooFinanceAPIError("No data for period")
    service = FinancialDataService(mock_provider_factory, mock_redis_client)
    with pytest.raises(FinancialDataServiceError, match="Failed to fetch historical data for IBM, period 1mo after trying all providers"):
        await service.get_historical_data("IBM", "1mo")
    mock_alpha_vantage_client.get_historical_data.assert_awaited_once_with("IBM", "1mo")
    mock_yahoo_finance_client.get_historical_data.assert_awaited_once_with("IBM", "1mo")
    mock_redis_client.get.assert_awaited_once()
    mock_redis_client.setex.assert_not_awaited()

@pytest.mark.asyncio
async def test_get_historical_data_from_cache(mock_provider_factory, mock_alpha_vantage_client, mock_redis_client):
    cached_hist_data = [HistoricalData(date="2023-01-01", open=90.0, high=95.0, low=89.0, close=93.0, volume=500000)]
    mock_redis_client.get.return_value = json.dumps([h.model_dump() for h in cached_hist_data]) # Simulate cached data
    service = FinancialDataService(mock_provider_factory, mock_redis_client)
    hist_data = await service.get_historical_data("GOOG", "1mo")

    mock_redis_client.get.assert_awaited_once()
    mock_alpha_vantage_client.get_historical_data.assert_not_awaited() # Provider should not be called
    mock_redis_client.setex.assert_not_awaited() # No cache write if read from cache

    assert len(hist_data) == 1
    assert hist_data[0].close == 93.0

@pytest.mark.asyncio
async def test_financial_data_service_no_providers_initialized(mock_redis_client):
    mock_factory = MagicMock(spec=DataProviderFactory)
    mock_factory.get_all_providers.return_value = {} # No providers
    with pytest.raises(FinancialDataServiceError, match="No active data providers available."):
        FinancialDataService(mock_factory, mock_redis_client)
