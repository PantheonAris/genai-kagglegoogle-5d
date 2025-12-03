from fastapi import FastAPI, HTTPException
from orchestrator.clients import AgentClients
from orchestrator.session import get_session_manager, SessionManager
from orchestrator.gemini import GeminiClient, RecognizedIntent
import os
from pydantic import BaseModel
from typing import Dict, Any
import structlog
from orchestrator.logging import configure_logging

configure_logging()
logger = structlog.get_logger()

app = FastAPI()

@app.on_event("startup")
async def startup_event():
    logger.info("Orchestrator starting up")

# In a real application, these URLs would come from a configuration service or environment variables.
BUDGET_AGENT_URL = os.getenv("BUDGET_AGENT_URL", "http://localhost:8001")
FINANCIAL_ANALYSIS_AGENT_URL = os.getenv("FINANCIAL_ANALYSIS_AGENT_URL", "http://localhost:8002")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

agent_clients = AgentClients(
    budget_agent_url=BUDGET_AGENT_URL,
    financial_analysis_agent_url=FINANCIAL_ANALYSIS_AGENT_URL
)

session_manager: SessionManager = get_session_manager()
gemini_client = GeminiClient(api_key=GEMINI_API_KEY)


class SessionData(BaseModel):
    session_id: str
    data: Dict[str, Any]

class IntentQuery(BaseModel):
    query: str

class OrchestrationResponse(BaseModel):
    response: str

@app.get("/health")
async def health_check():
    logger.info("Health check endpoint called")
    return {"status": "ok"}

@app.post("/orchestrate", response_model=OrchestrationResponse)
async def orchestrate(query: IntentQuery):
    logger.info("Orchestrating query", user_query=query.query)
    # 1. Recognize intent
    recognized_intent = gemini_client.recognize_intent(query.query)
    intent = recognized_intent.intent
    entities = recognized_intent.entities
    logger.info("Intent recognized", intent=intent, entities=entities)

    # 2. Delegate to the appropriate agent
    try:
        tool_results: Dict[str, Any] = {}
        if intent == "get_budget_advice":
            tool_results = await agent_clients.budget.post("/budget/calculate-50-30-20", data=entities)
        elif intent == "analyze_spending":
            tool_results = await agent_clients.budget.post("/budget/analyze-spending", data=entities)
        elif intent == "get_stock_data":
            tool_results = await agent_clients.financial_analysis.post("/financial/stock-data", data=entities)
        elif intent == "recommend_portfolio":
            tool_results = await agent_clients.financial_analysis.post("/financial/recommend-portfolio", data=entities)
        elif intent == "compare_stocks":
            tool_results = await agent_clients.financial_analysis.post("/financial/compare-stocks", data=entities)
        else: # unknown intent
            tool_results = {"message": "I'm sorry, I don't understand that request."}
        
        logger.info("Tool results", results=tool_results)

        # 3. Synthesize the response
        final_response = gemini_client.synthesize_response(query.query, tool_results)
        logger.info("Response synthesized")
        return OrchestrationResponse(response=final_response)

    except Exception as e:
        logger.exception("Error during orchestration")
        raise HTTPException(status_code=500, detail=f"Error during orchestration: {e}")


@app.post("/orchestrate/intent", response_model=RecognizedIntent)
async def recognize_intent_endpoint(query: IntentQuery):
    logger.info("Recognizing intent via dedicated endpoint", user_query=query.query)
    try:
        recognized_intent = gemini_client.recognize_intent(query.query)
        return recognized_intent
    except Exception as e:
        logger.exception("Error recognizing intent")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/orchestrate/budget-analysis")
async def orchestrate_budget_analysis(income: float):
    logger.info("Orchestrating budget analysis via dedicated endpoint", income=income)
    try:
        budget_data = {"monthly_income": income}
        result = await agent_clients.budget.post("/budget/calculate-50-30-20", data=budget_data)
        return result
    except Exception as e:
        logger.exception("Error orchestrating budget analysis")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/session/save")
async def save_session_endpoint(session_data: SessionData):
    logger.info("Saving session data", session_id=session_data.session_id)
    try:
        await session_manager.save_session(session_data.session_id, session_data.data)
        return {"status": "ok"}
    except Exception as e:
        logger.exception("Error saving session data")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/session/get/{session_id}")
async def get_session_endpoint(session_id: str):
    logger.info("Retrieving session data", session_id=session_id)
    try:
        session_data = await session_manager.get_session(session_id)
        if session_data is None:
            logger.warning("Session not found", session_id=session_id)
            raise HTTPException(status_code=404, detail="Session not found")
        return session_data
    except Exception as e:
        logger.exception("Error retrieving session data")
        raise HTTPException(status_code=500, detail=str(e))
