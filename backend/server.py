from fastapi import FastAPI, APIRouter, HTTPException, Depends, Request, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
import uuid

# Import our models and services
from models.financial_models import (
    User, UserCreate, Account, AccountCreate, Transaction, TransactionCreate,
    Budget, BudgetCreate, FinancialGoal, GoalCreate, AIInsight, FinancialHealthScore,
    FinancialDashboard, AccountsResponse, TransactionsResponse, BudgetResponse
)
from services.database_service import DatabaseService
from services.ai_service import AIFinancialAnalysisService
from services.plaid_service import PlaidIntegrationService

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# Initialize services
db_service = DatabaseService()
ai_service = AIFinancialAnalysisService()
plaid_service = PlaidIntegrationService(db_service)

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app
app = FastAPI(
    title="AI Financial Super-App",
    description="Billion-dollar AI-powered personal finance platform with smart insights and recommendations",
    version="1.0.0"
)

# Create API router with /api prefix
api_router = APIRouter(prefix="/api")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)
# Initialize database indexes on startup
@app.on_event("startup")
async def startup_event():
    await db_service.create_indexes()
    logger.info("AI Financial Super-App backend started successfully")

@app.on_event("shutdown")
async def shutdown_event():
    await db_service.close_connection()
    client.close()

# ============================================================================
# USER MANAGEMENT ENDPOINTS
# ============================================================================

@api_router.post("/users", response_model=User)
async def create_user(user_data: UserCreate):
    """Create a new user account."""
    try:
        # Check if user already exists
        existing_user = await db_service.get_user_by_email(user_data.email)
        if existing_user:
            raise HTTPException(status_code=400, detail="User with this email already exists")
        
        # Create new user
        user = User(**user_data.dict())
        created_user = await db_service.create_user(user)
        
        logger.info(f"Created new user: {created_user.id}")
        return created_user
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating user: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create user")

@api_router.get("/users/{user_id}", response_model=User)
async def get_user(user_id: str):
    """Get user by ID."""
    user = await db_service.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@api_router.get("/users/by-email/{email}", response_model=User)
async def get_user_by_email(email: str):
    """Get user by email."""
    user = await db_service.get_user_by_email(email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

# ============================================================================
# ACCOUNT MANAGEMENT ENDPOINTS
# ============================================================================

@api_router.post("/users/{user_id}/accounts", response_model=Account)
async def create_account(user_id: str, account_data: AccountCreate):
    """Create a new account for a user."""
    try:
        # Verify user exists
        user = await db_service.get_user_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Create account
        account = Account(user_id=user_id, **account_data.dict())
        created_account = await db_service.create_account(account)
        
        logger.info(f"Created account {created_account.id} for user {user_id}")
        return created_account
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating account: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create account")

@api_router.get("/users/{user_id}/accounts", response_model=AccountsResponse)
async def get_user_accounts(user_id: str):
    """Get all accounts for a user."""
    try:
        accounts = await db_service.get_user_accounts(user_id)
        total_balance = sum(acc.balance_current for acc in accounts)
        
        return AccountsResponse(
            accounts=accounts,
            total_balance=total_balance,
            total_count=len(accounts)
        )
        
    except Exception as e:
        logger.error(f"Error fetching accounts: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch accounts")
@api_router.get("/accounts/{account_id}", response_model=Account)
async def get_account(account_id: str):
    """Get account by ID."""
    account = await db_service.get_account_by_id(account_id)
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    return account

# ============================================================================
# TRANSACTION MANAGEMENT ENDPOINTS
# ============================================================================

@api_router.post("/users/{user_id}/transactions", response_model=Transaction)
async def create_transaction(user_id: str, transaction_data: TransactionCreate):
    """Create a new transaction."""
    try:
        # Verify account belongs to user
        account = await db_service.get_account_by_id(transaction_data.account_id)
        if not account or account.user_id != user_id:
            raise HTTPException(status_code=403, detail="Account does not belong to user")
        
        # Create transaction
        transaction = Transaction(user_id=user_id, **transaction_data.dict())
        created_transaction = await db_service.create_transaction(transaction)
        
        logger.info(f"Created transaction {created_transaction.id} for user {user_id}")
        return created_transaction
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating transaction: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create transaction")

@api_router.get("/users/{user_id}/transactions", response_model=TransactionsResponse)
async def get_user_transactions(
    user_id: str,
    limit: int = 100,
    skip: int = 0,
    account_id: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
):
    """Get transactions for a user with optional filters."""
    try:
        # Parse dates if provided
        start_dt = datetime.fromisoformat(start_date) if start_date else None
        end_dt = datetime.fromisoformat(end_date) if end_date else None
        
        transactions = await db_service.get_user_transactions(
            user_id=user_id,
            limit=limit,
            skip=skip,
            account_id=account_id,
            start_date=start_dt,
            end_date=end_dt
        )
        
        return TransactionsResponse(
            transactions=transactions,
            total_count=len(transactions),
            has_more=len(transactions) == limit
        )
        
    except Exception as e:
        logger.error(f"Error fetching transactions: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch transactions")

# ============================================================================
# AI INSIGHTS AND ANALYSIS ENDPOINTS  
# ============================================================================

@api_router.post("/users/{user_id}/analyze-spending")
async def analyze_spending_patterns(user_id: str, background_tasks: BackgroundTasks):
    """Trigger AI analysis of user's spending patterns."""
    try:
        # Get user's recent transactions
        transactions = await db_service.get_user_transactions(user_id, limit=500)
        
        if not transactions:
            raise HTTPException(status_code=400, detail="No transactions found for analysis")
        
        # Generate AI insights
        insights = await ai_service.analyze_spending_patterns(user_id, transactions)
        
        # Save insights to database
        if insights:
            await db_service.create_ai_insights_bulk(insights)
        
        return {"message": f"Generated {len(insights)} spending insights", "insights": insights}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing spending patterns: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to analyze spending patterns")
      @api_router.post("/users/{user_id}/calculate-financial-health")
async def calculate_financial_health_score(user_id: str):
    """Calculate comprehensive financial health score."""
    try:
        # Get user data
        accounts = await db_service.get_user_accounts(user_id)
        transactions = await db_service.get_user_transactions(user_id, limit=500)
        budgets = await db_service.get_user_budgets(user_id)
        goals = await db_service.get_user_goals(user_id)
        
        # Calculate health score
        health_score = await ai_service.calculate_financial_health_score(
            user_id, accounts, transactions, budgets, goals
        )
        
        # Save to database
        await db_service.save_financial_health_score(health_score)
        
        # Update user's health score
        await db_service.update_user(user_id, {
            'financial_health_score': health_score.overall_score,
            'last_analysis_date': datetime.utcnow()
        })
        
        return health_score
        
    except Exception as e:
        logger.error(f"Error calculating financial health score: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to calculate financial health score")

@api_router.get("/users/{user_id}/insights")
async def get_user_insights(user_id: str, limit: int = 20, unread_only: bool = False):
    """Get AI insights for a user."""
    try:
        insights = await db_service.get_user_insights(user_id, limit, unread_only)
        return insights
        
    except Exception as e:
        logger.error(f"Error fetching insights: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch insights")

# ============================================================================
# COMPREHENSIVE DASHBOARD ENDPOINT
# ============================================================================

@api_router.get("/users/{user_id}/dashboard", response_model=FinancialDashboard)
async def get_financial_dashboard(user_id: str):
    """Get comprehensive financial dashboard for a user."""
    try:
        # Get user
        user = await db_service.get_user_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Get all user data
        accounts = await db_service.get_user_accounts(user_id)
        transactions = await db_service.get_user_transactions(user_id, limit=50)
        budgets = await db_service.get_user_budgets(user_id)
        goals = await db_service.get_user_goals(user_id)
        insights = await db_service.get_user_insights(user_id, limit=10)
        health_score = await db_service.get_latest_financial_health_score(user_id)
        
        # Calculate summary metrics
        total_balance = sum(acc.balance_current for acc in accounts)
        
        # Calculate monthly cash flow
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        recent_transactions = [t for t in transactions if t.transaction_date >= thirty_days_ago]
        monthly_income = sum(t.amount for t in recent_transactions if t.amount > 0)
        monthly_expenses = sum(abs(t.amount) for t in recent_transactions if t.amount < 0)
        monthly_cash_flow = monthly_income - monthly_expenses
        
        # Build dashboard
        dashboard = FinancialDashboard(
            user=user,
            accounts_summary=AccountsResponse(
                accounts=accounts,
                total_balance=total_balance,
                total_count=len(accounts)
            ),
            recent_transactions=transactions[:10],
            active_budgets=budgets,
            financial_goals=goals,
            financial_health_score=health_score,
            ai_insights=insights,
            monthly_spending_by_category={},
            net_worth=total_balance,
            monthly_cash_flow=monthly_cash_flow
        )
        
        return dashboard
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error building dashboard: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to build dashboard")

# ============================================================================
# PLAID ENDPOINTS & HEALTH CHECK
# ============================================================================

@api_router.post("/users/{user_id}/plaid/create-link-token")
async def create_plaid_link_token(user_id: str):
    """Create a Plaid Link token for bank account connection."""
    try:
        user = await db_service.get_user_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        link_token_data = await plaid_service.create_link_token(user_id)
        return link_token_data
        
    except Exception as e:
        logger.error(f"Error creating Plaid link token: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/")
async def root():
    return {
        "message": "AI Financial Super-App API",
        "version": "1.0.0",
        "status": "operational",
        "features": [
            "AI-powered financial insights",
            "Smart budgeting recommendations", 
            "Financial health scoring",
            "Goal tracking and analysis",
            "Comprehensive financial dashboard"
        ]
    }

@api_router.get("/health")
async def health_check():
    """Health check endpoint."""
    try:
        await db.command("ping")
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "database": "connected",
            "ai_service": "ready"
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(status_code=503, detail="Service unavailable")

# Include the router in the main app
app.include_router(api_router)

# Shutdown handler
@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
