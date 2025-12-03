import pytest
from unittest.mock import AsyncMock, patch, MagicMock
import httpx
from financial_analysis_agent.clients.alpha_vantage import AlphaVantageClient, AlphaVantageAPIError
from financial_analysis_agent.clients.data_provider import Quote, HistoricalData

# Mock API Key for testing
TEST_API_KEY = "test_api_key"

@pytest.fixture
def alpha_vantage_client():
    """Fixture to provide an AlphaVantageClient instance."""
    return AlphaVantageClient(api_key=TEST_API_KEY)

@pytest.mark.asyncio
async def test_get_quote_success(alpha_vantage_client):
    mock_response_data = {
        "Global Quote": {
            "01. symbol": "IBM",
            "02. open": "150.0000",
            "03. high": "152.0000",
            "04. low": "149.5000",
            "05. price": "151.5000",
            "06. volume": "1000000",
            "07. latest trading day": "2023-11-20",
            "08. previous close": "149.0000",
            "09. change": "2.5000",
            "10. change percent": "1.6779%"
        }
    }
    with patch('httpx.AsyncClient.get', new_callable=AsyncMock) as mock_get:
        mock_response = AsyncMock()
        mock_response.json.return_value = mock_response_data
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        quote = await alpha_vantage_client.get_quote("IBM")

        assert isinstance(quote, Quote)
        assert quote.symbol == "IBM"
        assert quote.price == 151.5
        assert quote.volume == 1000000
        mock_get.assert_called_once()
        assert mock_get.call_args.kwargs['params']['function'] == "GLOBAL_QUOTE"
        assert mock_get.call_args.kwargs['params']['symbol'] == "IBM"
        assert mock_get.call_args.kwargs['params']['apikey'] == TEST_API_KEY

@pytest.mark.asyncio
async def test_get_quote_api_error(alpha_vantage_client):
    with patch('financial_analysis_agent.clients.alpha_vantage.AlphaVantageClient._make_request', new_callable=AsyncMock) as mock_make_request:
        mock_make_request.side_effect = AlphaVantageAPIError("Invalid API call. Please retry or visit the documentation.")
        
        with pytest.raises(AlphaVantageAPIError, match="Invalid API call"):
            await alpha_vantage_client.get_quote("INVALID")
        mock_make_request.assert_called_once()
        assert mock_make_request.call_args.args[0]['symbol'] == "INVALID"

@pytest.mark.asyncio
async def test_get_quote_no_data(alpha_vantage_client):
    with patch('financial_analysis_agent.clients.alpha_vantage.AlphaVantageClient._make_request', new_callable=AsyncMock) as mock_make_request:
        mock_make_request.side_effect = AlphaVantageAPIError("Thank you for using Alpha Vantage! Our standard API call frequency is 5 calls per minute and 500 calls per day. Please visit https://www.alphavantage.co/premium/ to upgrade your rate limit.")

        with pytest.raises(AlphaVantageAPIError, match="API call frequency is 5 calls per minute"):
            await alpha_vantage_client.get_quote("IBM")
        mock_make_request.assert_called_once()
        assert mock_make_request.call_args.args[0]['symbol'] == "IBM"

@pytest.mark.asyncio
async def test_get_quote_http_error(alpha_vantage_client):
    with patch('financial_analysis_agent.clients.alpha_vantage.AlphaVantageClient._make_request', new_callable=AsyncMock) as mock_make_request:
        mock_make_request.side_effect = AlphaVantageAPIError("HTTP error occurred: 400 - Bad Request")

        with pytest.raises(AlphaVantageAPIError, match="HTTP error occurred: 400 - Bad Request"):
            await alpha_vantage_client.get_quote("IBM")
        mock_make_request.assert_called_once()
        assert mock_make_request.call_args.args[0]['symbol'] == "IBM"

@pytest.mark.asyncio
async def test_get_historical_data_success(alpha_vantage_client):
    mock_response_data = {
        "Meta Data": {
            "1. Information": "Daily Prices and Volumes for Digital Currency",
            "2. Digital Currency Code": "BTC",
            "3. Digital Currency Name": "Bitcoin",
            "4. Market Code": "USD",
            "5. Market Name": "United States Dollar",
            "6. Last Refreshed": "2023-11-20 15:30:00",
            "7. Time Zone": "UTC"
        },
        "Time Series (Daily)": {
            "2023-11-20": {
                "1. open": "37500.00",
                "2. high": "37800.00",
                "3. low": "37400.00",
                "4. close": "37700.00",
                "5. volume": "5000"
            },
            "2023-11-19": {
                "1. open": "37000.00",
                "2. high": "37200.00",
                "3. low": "36900.00",
                "4. close": "37100.00",
                "5. volume": "4500"
            }
        }
    }
    with patch('httpx.AsyncClient.get', new_callable=AsyncMock) as mock_get:
        mock_response = AsyncMock()
        mock_response.json.return_value = mock_response_data
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        historical_data = await alpha_vantage_client.get_historical_data("BTC", "compact")

        assert isinstance(historical_data, list)
        assert len(historical_data) == 2
        assert all(isinstance(data, HistoricalData) for data in historical_data)
        assert historical_data[0].date == "2023-11-20"
        assert historical_data[0].close == 37700.00
        mock_get.assert_called_once()
        assert mock_get.call_args.kwargs['params']['function'] == "TIME_SERIES_DAILY"
        assert mock_get.call_args.kwargs['params']['symbol'] == "BTC"
        assert mock_get.call_args.kwargs['params']['apikey'] == TEST_API_KEY

@pytest.mark.asyncio
async def test_get_daily_historical_data_api_error(alpha_vantage_client):
    with patch('financial_analysis_agent.clients.alpha_vantage.AlphaVantageClient._make_request', new_callable=AsyncMock) as mock_make_request:
        mock_make_request.side_effect = AlphaVantageAPIError("the parameter symbol is invalid")

        with pytest.raises(AlphaVantageAPIError, match="the parameter symbol is invalid"):
            await alpha_vantage_client.get_historical_data("INVALID_SYMBOL", "compact")
        mock_make_request.assert_called_once()
        assert mock_make_request.call_args.args[0]['symbol'] == "INVALID_SYMBOL"

@pytest.mark.asyncio
async def test_get_daily_historical_data_no_data(alpha_vantage_client):
    with patch('financial_analysis_agent.clients.alpha_vantage.AlphaVantageClient._make_request', new_callable=AsyncMock) as mock_make_request:
        mock_make_request.side_effect = AlphaVantageAPIError("Thank you for using Alpha Vantage! Our standard API call frequency is 5 calls per minute and 500 calls per day. Please visit https://www.alphavantage.co/premium/ to upgrade your rate limit.")

        with pytest.raises(AlphaVantageAPIError, match="API call frequency is 5 calls per minute"):
            await alpha_vantage_client.get_historical_data("IBM", "compact")
        mock_make_request.assert_called_once()
        assert mock_make_request.call_args.args[0]['symbol'] == "IBM"

