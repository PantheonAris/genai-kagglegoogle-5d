from pydantic import BaseModel, Field
from typing import List, Dict

class IncomeInput(BaseModel):
    monthly_income: float = Field(..., gt=0, description="User's monthly income.")

class BudgetOutput(BaseModel):
    monthly_income: float
    needs: float
    wants: float
    savings: float
    needs_percentage: float = 50.0
    wants_percentage: float = 30.0
    savings_percentage: float = 20.0

class SpendingCategory(BaseModel):
    name: str = Field(..., description="Name of the spending category (e.g., 'Dining Out', 'Groceries').")
    amount: float = Field(..., gt=0, description="Amount spent in this category.")

class SpendingAnalysisInput(BaseModel):
    monthly_income: float = Field(..., gt=0, description="User's monthly income.")
    spending: List[SpendingCategory] = Field(..., description="List of spending categories and amounts.")

class SpendingRecommendation(BaseModel):
    category: str = Field(..., description="The spending category for the recommendation.")
    recommendation: str = Field(..., description="Actionable advice for the category.")
    potential_savings: float = Field(..., ge=0, description="Estimated potential savings from this recommendation.")

class SpendingAnalysisOutput(BaseModel):
    total_spending: float
    spending_by_category: Dict[str, float]
    budget_adherence: Dict[str, float]
    recommendations: List[SpendingRecommendation]
    summary: str
