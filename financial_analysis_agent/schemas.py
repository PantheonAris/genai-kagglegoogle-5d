from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from financial_analysis_agent.clients.data_provider import Quote, HistoricalData

class StockDataInput(BaseModel):
    symbol: str = Field(..., description="Stock ticker symbol (e.g., 'AAPL', 'IBM').")
    period: Optional[str] = Field(None, description="Time period for historical data (e.g., '1mo', '1y'). Leave None for only quote.")

class StockDataOutput(BaseModel):
    quote: Optional[Quote] = Field(None, description="Current stock quote.")
    historical_data: Optional[List[HistoricalData]] = Field(None, description="Historical stock data.")

class PortfolioRecommendationInput(BaseModel):
    risk_tolerance: str = Field(..., description="User's risk tolerance (e.g., 'conservative', 'moderate', 'aggressive').")
    investment_amount: float = Field(..., gt=0, description="Amount to invest.")
    time_horizon: int = Field(..., gt=0, description="Investment time horizon in years.")

class PortfolioAsset(BaseModel):
    symbol: str
    asset_class: str
    allocation: float = Field(..., ge=0, le=100, description="Percentage allocation of this asset.")

class PortfolioRecommendationOutput(BaseModel):
    risk_profile: str
    description: str
    recommended_portfolio: List[PortfolioAsset]

class CompareStocksInput(BaseModel):
    symbols: List[str] = Field(..., description="List of stock symbols to compare.")
    period: str = Field("1y", description="Time period for comparison (e.g., '1mo', '1y').")

class StockPerformance(BaseModel):
    symbol: str
    start_price: float
    end_price: float
    change: float
    change_percent: float

class CompareStocksOutput(BaseModel):
    period: str
    performance_comparison: List[StockPerformance]

