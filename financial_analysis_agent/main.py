from fastapi import FastAPI, HTTPException
from financial_analysis_agent.services.financial_data_service import FinancialDataService, FinancialDataServiceError
from financial_analysis_agent.clients.data_provider_factory import DataProviderFactory
from financial_analysis_agent.schemas import StockDataInput, StockDataOutput, PortfolioRecommendationInput, PortfolioRecommendationOutput, CompareStocksInput, CompareStocksOutput
from financial_analysis_agent.services.portfolio_service import PortfolioService
import redis.asyncio as redis
import os
import structlog
from financial_analysis_agent.logging import configure_logging

configure_logging()
logger = structlog.get_logger()

app = FastAPI()

@app.on_event("startup")
async def startup_event():
    logger.info("Financial Analysis Agent starting up")

# Configuration for Redis (from environment variables)
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_DB = int(os.getenv("REDIS_DB", 0))

# Configuration for API keys (from environment variables or Secret Manager)
ALPHA_VANTAGE_API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY")
# YAHOO_FINANCE_API_KEY - yfinance does not typically use an API key

def get_financial_data_service() -> FinancialDataService:
    """
    Initializes and returns the FinancialDataService.
    This function is designed to be easily patched for testing.
    """
    # Initialize Redis client
    # In a real Cloud Run environment, this might be a connection pool.
    redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB)

    # Initialize data providers
    api_keys = {
        "ALPHA_VANTAGE_API_KEY": ALPHA_VANTAGE_API_KEY,
    }
    provider_factory = DataProviderFactory(api_keys=api_keys)
    service = FinancialDataService(provider_factory=provider_factory, redis_client=redis_client)
    return service

# Initialize the service globally, but allow patching get_financial_data_service
financial_data_service = get_financial_data_service()
portfolio_service = PortfolioService()

@app.get("/health")
async def health_check():
    logger.info("Health check endpoint called")
    return {"status": "ok"}

@app.post("/financial/stock-data", response_model=StockDataOutput)
async def get_stock_data(input: StockDataInput):
    logger.info("Getting stock data", symbol=input.symbol, period=input.period)
    quote = None
    historical_data = None
    errors = []

    try:
        # Always try to get the quote
        quote = await financial_data_service.get_quote(input.symbol)
    except FinancialDataServiceError as e:
        logger.error("Error fetching quote", error=e, symbol=input.symbol)
        errors.append(f"Error fetching quote: {e}")
    except Exception as e:
        logger.exception("Unexpected error fetching quote", symbol=input.symbol)
        errors.append(f"Unexpected error fetching quote: {e}")

    if input.period:
        try:
            historical_data = await financial_data_service.get_historical_data(input.symbol, input.period)
        except FinancialDataServiceError as e:
            logger.error("Error fetching historical data", error=e, symbol=input.symbol, period=input.period)
            errors.append(f"Error fetching historical data: {e}")
        except Exception as e:
            logger.exception("Unexpected error fetching historical data", symbol=input.symbol, period=input.period)
            errors.append(f"Unexpected error fetching historical data: {e}")
    
    if not quote and not historical_data and errors:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve any data: {'; '.join(errors)}")
    elif errors:
        # If some data was retrieved but there were errors, return partial data with a warning
        logger.warning("Partial data retrieved with errors", symbol=input.symbol, errors=errors)


    return StockDataOutput(quote=quote, historical_data=historical_data)

@app.post("/financial/recommend-portfolio", response_model=PortfolioRecommendationOutput)
async def recommend_portfolio(input: PortfolioRecommendationInput):
    logger.info("Recommending portfolio", risk_tolerance=input.risk_tolerance)
    try:
        recommendation = portfolio_service.recommend_portfolio(input)
        return recommendation
    except Exception as e:
        logger.exception("Failed to generate portfolio recommendation")
        raise HTTPException(status_code=500, detail=f"Failed to generate portfolio recommendation: {e}")

@app.post("/financial/compare-stocks", response_model=CompareStocksOutput)
async def compare_stocks(input: CompareStocksInput):
    logger.info("Comparing stocks", symbols=input.symbols, period=input.period)
    try:
        performance_comparison = await financial_data_service.compare_stocks(input.symbols, input.period)
        return CompareStocksOutput(
            period=input.period,
            performance_comparison=performance_comparison
        )
    except FinancialDataServiceError as e:
        logger.error("Error comparing stocks", error=e, symbols=input.symbols)
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.exception("An unexpected error occurred during stock comparison", symbols=input.symbols)
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred during stock comparison: {e}")
