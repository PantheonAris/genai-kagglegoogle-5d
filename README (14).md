# Multi-Agent Financial Advisory System

This project is a multi-agent financial advisory system that provides personalized financial advice to users. It leverages the power of Large Language Models (LLMs) through a set of specialized agents coordinated by an orchestrator.

## Overview

The system is composed of three main agents:
- **Orchestrator Agent**: The main entry point that routes user requests to the appropriate specialized agent.
- **Budget Agent**: Specializes in personal budgeting, spending analysis, and financial discipline.
- **Financial Analysis Agent**: Focuses on investment research, portfolio management, and market analysis.

## Tech Stack

- **Cloud Platform**: Google Cloud Platform (GCP)
- **AI/LLM**: Google Gemini
- **Deployment**: Cloud Run
- **Backend**: Python with FastAPI
- **Session Management**: Google Cloud Memorystore (Redis)
- **Data Sources**: Alpha Vantage and Yahoo Finance for financial data.

## Project Structure

The project is organized as a monorepo with the following structure:
```
/
├── orchestrator/         # Code for the Orchestrator Agent
├── budget_agent/         # Code for the Budget Agent
├── financial_analysis_agent/ # Code for the Financial Analysis Agent
├── design_v2.md
├── requirements_v2.md
├── tasks_detailed_v2.md
└── ...
```

## Getting Started

*(Instructions for setup, deployment, and usage will be added here.)*
