from fastapi import FastAPI, HTTPException
from budget_agent.schemas import (
    IncomeInput, 
    BudgetOutput, 
    SpendingAnalysisInput, 
    SpendingAnalysisOutput, 
    SpendingCategory,
    SpendingRecommendation
)
from typing import List, Dict
from budget_agent.logging import configure_logging
import structlog

configure_logging()
logger = structlog.get_logger()

app = FastAPI()

@app.on_event("startup")
async def startup_event():
    logger.info("Budget Agent starting up")

@app.get("/health")
async def health_check():
    logger.info("Health check endpoint called")
    return {"status": "ok"}

@app.post("/budget/calculate-50-30-20", response_model=BudgetOutput)
async def calculate_50_30_20_budget(income_input: IncomeInput):
    logger.info("Calculating 50/30/20 budget", income=income_input.monthly_income)
    monthly_income = income_input.monthly_income
    
    needs = monthly_income * 0.50
    wants = monthly_income * 0.30
    savings = monthly_income * 0.20
    
    return BudgetOutput(
        monthly_income=monthly_income,
        needs=needs,
        wants=wants,
        savings=savings,
        needs_percentage=50.0,
        wants_percentage=30.0,
        savings_percentage=20.0,
    )

@app.post("/budget/analyze-spending", response_model=SpendingAnalysisOutput)
async def analyze_spending(analysis_input: SpendingAnalysisInput):
    logger.info("Analyzing spending", income=analysis_input.monthly_income, num_items=len(analysis_input.spending))
    monthly_income = analysis_input.monthly_income
    spending_items = analysis_input.spending

    # Calculate total spending
    total_spending = sum(item.amount for item in spending_items)

    # Calculate spending by category
    spending_by_category: Dict[str, float] = {}
    for item in spending_items:
        spending_by_category[item.name] = spending_by_category.get(item.name, 0.0) + item.amount

    # Apply 50/30/20 rule for comparison
    budget_needs_limit = monthly_income * 0.50
    budget_wants_limit = monthly_income * 0.30
    budget_savings_target = monthly_income * 0.20

    # Basic Budget Adherence (can be expanded)
    # For simplicity, let's assume 'Needs' categories are essential and 'Wants' are discretionary
    # This categorization would ideally come from a more sophisticated system or user input
    # For now, let's just compare total spending against the 'Needs' + 'Wants' portion of the budget
    
    # Simple heuristic: If total spending exceeds 80% of income, provide general warning
    budget_adherence: Dict[str, float] = {
        "needs_limit": budget_needs_limit,
        "wants_limit": budget_wants_limit,
        "savings_target": budget_savings_target,
        "total_spending_vs_income_percentage": (total_spending / monthly_income) * 100 if monthly_income > 0 else 0
    }

    recommendations: List[SpendingRecommendation] = []
    summary_messages: List[str] = []

    if total_spending > (budget_needs_limit + budget_wants_limit):
        overspend_amount = total_spending - (budget_needs_limit + budget_wants_limit)
        summary_messages.append(f"Your total spending of ${total_spending:.2f} exceeds your combined needs and wants budget of ${budget_needs_limit + budget_wants_limit:.2f} by ${overspend_amount:.2f}. This leaves no room for savings.")
        recommendations.append(
            SpendingRecommendation(
                category="General Spending",
                recommendation="Review all discretionary spending to find areas to cut back to meet your savings goals.",
                potential_savings=overspend_amount
            )
        )
    elif total_spending > budget_needs_limit:
        # Check if "Wants" categories are contributing to high spending
        # This is a very basic example; a real system would need more intelligence
        sorted_spending = sorted(spending_by_category.items(), key=lambda item: item[1], reverse=True)
        top_category, top_amount = sorted_spending[0] if sorted_spending else ("", 0)

        if top_category and top_amount > (monthly_income * 0.10): # Arbitrary threshold for high spending category
            recommendations.append(
                SpendingRecommendation(
                    category=top_category,
                    recommendation=f"Your spending in '{top_category}' is ${top_amount:.2f}. Consider reducing this by 10-20% to free up funds for savings or other goals.",
                    potential_savings=top_amount * 0.15 # Example potential saving
                )
            )
        summary_messages.append(f"Your total spending is ${total_spending:.2f}. You are within your 'needs' and 'wants' allocation, but could optimize further to maximize savings.")
    else:
        summary_messages.append(f"Your spending of ${total_spending:.2f} is well within your 'needs' and 'wants' budget. Great job! Consider allocating more to savings or investments.")

    # Example: Specific recommendation for "Dining Out" if it's high
    dining_out_spending = spending_by_category.get("Dining Out", 0.0)
    if dining_out_spending > (monthly_income * 0.05): # If dining out is more than 5% of income
        recommendations.append(
            SpendingRecommendation(
                category="Dining Out",
                recommendation=f"Your 'Dining Out' spending is ${dining_out_spending:.2f}. Try reducing it by 25% (e.g., eat out once less per week) to save an estimated ${dining_out_spending * 0.25:.2f}.",
                potential_savings=dining_out_spending * 0.25
            )
        )

    return SpendingAnalysisOutput(
        total_spending=total_spending,
        spending_by_category=spending_by_category,
        budget_adherence=budget_adherence,
        recommendations=recommendations,
        summary=" ".join(summary_messages)
    )
