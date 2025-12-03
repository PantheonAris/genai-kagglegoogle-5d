import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch, MagicMock
from financial_analysis_agent.main import app, get_financial_data_service
from financial_analysis_agent.services.financial_data_service import FinancialDataService, FinancialDataServiceError
from financial_analysis_agent.schemas import StockDataInput, StockDataOutput
from financial_analysis_agent.clients.data_provider import Quote, HistoricalData

client = TestClient(app)

@pytest.fixture
def mock_financial_data_service_instance():
    """Fixture to provide a mock FinancialDataService instance."""
    mock = AsyncMock(spec=FinancialDataService)
    # Default successful behavior for individual tests to override
    mock.get_quote.return_value = Quote(symbol="AAPL", price=170.0, currency="USD")
    mock.get_historical_data.return_value = [
        HistoricalData(date="2023-01-01", open=160.0, high=161.0, low=159.0, close=160.5, volume=1000000)
    ]
    return mock

@pytest.fixture(autouse=True, scope="function")
def mock_main_financial_data_service(mock_financial_data_service_instance):
    """
    Fixture to patch the globally initialized financial_data_service in main.py
    with a mock instance for each test function.
    """
    with patch('financial_analysis_agent.main.financial_data_service', new=mock_financial_data_service_instance):
        yield

@pytest.mark.asyncio
async def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

@pytest.mark.asyncio
async def test_get_stock_data_both_quote_and_historical(mock_financial_data_service_instance: AsyncMock):
    # No need to patch get_financial_data_service explicitly, mock_main_financial_data_service handles it
    # Setup mock behavior (already done in fixture, just ensuring clarity)
    mock_financial_data_service_instance.get_quote.return_value = Quote(symbol="AAPL", price=170.0, currency="USD")
    mock_financial_data_service_instance.get_historical_data.return_value = [
        HistoricalData(date="2023-01-01", open=160.0, high=161.0, low=159.0, close=160.5, volume=1000000)
    ]

    input_data = StockDataInput(symbol="AAPL", period="1mo")
    response = client.post(
        "/financial/stock-data",
        json=input_data.model_dump()
    )

    assert response.status_code == 200
    output = StockDataOutput(**response.json())

    assert output.quote is not None
    assert output.quote.symbol == "AAPL"
    assert output.quote.price == 170.0
    assert output.historical_data is not None
    mock_financial_data_service_instance.get_quote.assert_awaited_once_with("AAPL")
    mock_financial_data_service_instance.get_historical_data.assert_awaited_once_with("AAPL", "1mo")

@pytest.mark.asyncio
async def test_get_stock_data_only_quote(mock_financial_data_service_instance: AsyncMock):
    mock_financial_data_service_instance.get_quote.return_value = Quote(symbol="AAPL", price=170.0, currency="USD")
    mock_financial_data_service_instance.get_historical_data.return_value = [] # Return empty list if no historical data

    input_data = StockDataInput(symbol="AAPL") # No period
    response = client.post(
        "/financial/stock-data",
        json=input_data.model_dump()
    )

    assert response.status_code == 200
    output = StockDataOutput(**response.json())

    assert output.quote is not None
    assert output.quote.symbol == "AAPL"
    assert output.historical_data is None # Should be None if not requested

    mock_financial_data_service_instance.get_quote.assert_awaited_once_with("AAPL")
    mock_financial_data_service_instance.get_historical_data.assert_not_awaited()

@pytest.mark.asyncio
async def test_get_stock_data_quote_fails_historical_succeeds(mock_financial_data_service_instance: AsyncMock):
    mock_financial_data_service_instance.get_quote.side_effect = FinancialDataServiceError("Quote service failed")
    mock_financial_data_service_instance.get_historical_data.return_value = [
        HistoricalData(date="2023-01-01", open=160.0, high=161.0, low=159.0, close=160.5, volume=1000000)
    ]

    input_data = StockDataInput(symbol="AAPL", period="1mo")
    response = client.post(
        "/financial/stock-data",
        json=input_data.model_dump()
    )

    assert response.status_code == 200 # Still 200 because historical data succeeded
    output = StockDataOutput(**response.json())

    assert output.quote is None
    assert output.historical_data is not None
    assert len(output.historical_data) == 1

    mock_financial_data_service_instance.get_quote.assert_awaited_once_with("AAPL")
    mock_financial_data_service_instance.get_historical_data.assert_awaited_once_with("AAPL", "1mo")
    # The error message from `print` statement is not part of the response detail when status is 200
    # The `detail` field is only present for HTTPException (status_code 500 in `all_fail` case)
    # The error is just logged.

@pytest.mark.asyncio
async def test_get_stock_data_all_fail(mock_financial_data_service_instance: AsyncMock):
    mock_financial_data_service_instance.get_quote.side_effect = FinancialDataServiceError("Quote service failed")
    mock_financial_data_service_instance.get_historical_data.side_effect = FinancialDataServiceError("Historical service failed")

    input_data = StockDataInput(symbol="AAPL", period="1mo")
    response = client.post(
        "/financial/stock-data",
        json=input_data.model_dump()
    )

    assert response.status_code == 500
    assert "Failed to retrieve any data" in response.json()["detail"]
    assert "Error fetching quote" in response.json()["detail"]
    assert "Error fetching historical data" in response.json()["detail"]

    mock_financial_data_service_instance.get_quote.assert_awaited_once_with("AAPL")
    mock_financial_data_service_instance.get_historical_data.assert_awaited_once_with("AAPL", "1mo")

@pytest.mark.asyncio
async def test_get_stock_data_invalid_symbol_pydantic_validation(): # No mock_get_financial_data_service here
    input_data = StockDataInput(symbol="", period="1mo") # Symbol cannot be empty
    response = client.post(
        "/financial/stock-data",
        json=input_data.model_dump()
    )
    assert response.status_code == 422 # Pydantic validation error
    # No service calls expected due to Pydantic validation catching it earlier
