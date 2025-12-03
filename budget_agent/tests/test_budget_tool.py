from fastapi.testclient import TestClient
from budget_agent.main import app
from budget_agent.schemas import IncomeInput, BudgetOutput, SpendingAnalysisInput, SpendingCategory, SpendingAnalysisOutput, SpendingRecommendation

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_calculate_50_30_20_budget_positive_income():
    income = 6000
    response = client.post(
        "/budget/calculate-50-30-20",
        json={"monthly_income": income}
    )
    assert response.status_code == 200
    
    expected_output = BudgetOutput(
        monthly_income=income,
        needs=3000.0,
        wants=1800.0,
        savings=1200.0,
        needs_percentage=50.0,
        wants_percentage=30.0,
        savings_percentage=20.0,
    )
    assert response.json() == expected_output.model_dump()

def test_calculate_50_30_20_budget_zero_income():
    income = 0
    response = client.post(
        "/budget/calculate-50-30-20",
        json={"monthly_income": income}
    )
    assert response.status_code == 422 # Unprocessable Entity due to gt=0 validation

def test_calculate_50_30_20_budget_negative_income():
    income = -1000
    response = client.post(
        "/budget/calculate-50-30-20",
        json={"monthly_income": income}
    )
    assert response.status_code == 422 # Unprocessable Entity due to gt=0 validation

# --- Spending Analysis Tool Tests ---
def test_analyze_spending_within_budget():
    income = 5000
    spending = [
        SpendingCategory(name="Rent", amount=2000),
        SpendingCategory(name="Groceries", amount=500),
        SpendingCategory(name="Utilities", amount=200),
        SpendingCategory(name="Dining Out", amount=300),
        SpendingCategory(name="Entertainment", amount=150),
    ]
    response = client.post(
        "/budget/analyze-spending",
        json={"monthly_income": income, "spending": [s.model_dump() for s in spending]}
    )
    assert response.status_code == 200
    output = SpendingAnalysisOutput(**response.json())

    assert output.total_spending == 3150
    assert output.summary == "Your total spending is $3150.00. You are within your 'needs' and 'wants' allocation, but could optimize further to maximize savings."
    
    # Assert specific recommendations are present
    assert len(output.recommendations) == 2
    rec_categories = {rec.category for rec in output.recommendations}
    assert "Rent" in rec_categories
    assert "Dining Out" in rec_categories

    rent_rec = next(rec for rec in output.recommendations if rec.category == "Rent")
    assert "Your spending in 'Rent' is $2000.00" in rent_rec.recommendation
    assert rent_rec.potential_savings == 300.0 # 15% of 2000

    dining_rec = next(rec for rec in output.recommendations if rec.category == "Dining Out")
    assert "Your 'Dining Out' spending is $300.00" in dining_rec.recommendation
    assert dining_rec.potential_savings == 75.0 # 25% of 300

def test_analyze_spending_over_budget_total():
    income = 5000
    spending = [
        SpendingCategory(name="Rent", amount=2500),
        SpendingCategory(name="Groceries", amount=800),
        SpendingCategory(name="Utilities", amount=300),
        SpendingCategory(name="Dining Out", amount=1000),
        SpendingCategory(name="Shopping", amount=1200),
    ]
    response = client.post(
        "/budget/analyze-spending",
        json={"monthly_income": income, "spending": [s.model_dump() for s in spending]}
    )
    assert response.status_code == 200
    output = SpendingAnalysisOutput(**response.json())

    assert output.total_spending == 5800
    assert "exceeds your combined needs and wants budget" in output.summary
    assert any(rec.category == "General Spending" for rec in output.recommendations)
    overspend_rec = next(rec for rec in output.recommendations if rec.category == "General Spending")
    assert overspend_rec.potential_savings == 1800.0 # 5800 - (2500+1500)

def test_analyze_spending_high_dining_out():
    income = 5000
    spending = [
        SpendingCategory(name="Rent", amount=2000),
        SpendingCategory(name="Groceries", amount=500),
        SpendingCategory(name="Utilities", amount=200),
        SpendingCategory(name="Dining Out", amount=800), # High dining out
        SpendingCategory(name="Entertainment", amount=150),
    ]
    response = client.post(
        "/budget/analyze-spending",
        json={"monthly_income": income, "spending": [s.model_dump() for s in spending]}
    )
    assert response.status_code == 200
    output = SpendingAnalysisOutput(**response.json())

    assert output.total_spending == 3650
    assert output.summary == "Your total spending is $3650.00. You are within your 'needs' and 'wants' allocation, but could optimize further to maximize savings."
    
    # Check for the specific Dining Out recommendation
    assert any(rec.category == "Dining Out" for rec in output.recommendations)
    dining_rec = next(rec for rec in output.recommendations if rec.category == "Dining Out")
    assert "Your 'Dining Out' spending is $800.00" in dining_rec.recommendation
    assert dining_rec.potential_savings == 200.0 # 25% of 800

def test_analyze_spending_with_zero_income():
    income = 0
    spending = [
        SpendingCategory(name="Rent", amount=1000)
    ]
    response = client.post(
        "/budget/analyze-spending",
        json={"monthly_income": income, "spending": [s.model_dump() for s in spending]}
    )
    assert response.status_code == 422 # income must be gt=0

