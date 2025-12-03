from financial_analysis_agent.schemas import PortfolioRecommendationInput, PortfolioRecommendationOutput, PortfolioAsset
from typing import Dict, List

class PortfolioService:
    def recommend_portfolio(self, input: PortfolioRecommendationInput) -> PortfolioRecommendationOutput:
        """
        Generates a simplified portfolio recommendation based on risk tolerance.
        """
        risk = input.risk_tolerance.lower()

        if risk == "conservative":
            description = "A conservative portfolio focused on capital preservation with modest growth."
            assets = [
                PortfolioAsset(symbol="BND", asset_class="Bond ETF", allocation=60.0),
                PortfolioAsset(symbol="VTI", asset_class="US Stock Market ETF", allocation=30.0),
                PortfolioAsset(symbol="VEA", asset_class="International Stock ETF", allocation=10.0),
            ]
        elif risk == "moderate":
            description = "A balanced portfolio with a mix of growth and stability."
            assets = [
                PortfolioAsset(symbol="VTI", asset_class="US Stock Market ETF", allocation=50.0),
                PortfolioAsset(symbol="VEA", asset_class="International Stock ETF", allocation=25.0),
                PortfolioAsset(symbol="BND", asset_class="Bond ETF", allocation=25.0),
            ]
        elif risk == "aggressive":
            description = "A growth-focused portfolio with higher potential returns and higher risk."
            assets = [
                PortfolioAsset(symbol="VTI", asset_class="US Stock Market ETF", allocation=60.0),
                PortfolioAsset(symbol="VEA", asset_class="International Stock ETF", allocation=30.0),
                PortfolioAsset(symbol="VWO", asset_class="Emerging Markets ETF", allocation=10.0),
            ]
        else:
            # Default to moderate if risk tolerance is unknown
            description = "A balanced portfolio with a mix of growth and stability."
            assets = [
                PortfolioAsset(symbol="VTI", asset_class="US Stock Market ETF", allocation=50.0),
                PortfolioAsset(symbol="VEA", asset_class="International Stock ETF", allocation=25.0),
                PortfolioAsset(symbol="BND", asset_class="Bond ETF", allocation=25.0),
            ]

        return PortfolioRecommendationOutput(
            risk_profile=input.risk_tolerance,
            description=description,
            recommended_portfolio=assets
        )
