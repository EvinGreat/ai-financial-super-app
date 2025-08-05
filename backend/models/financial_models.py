from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
import uuid
from enum import Enum

# Database Models for Financial Data

class AccountType(str, Enum):
    CHECKING = "checking"
    SAVINGS = "savings"
    CREDIT_CARD = "credit"
    INVESTMENT = "investment"
    LOAN = "loan"
    MORTGAGE = "mortgage"

class TransactionCategory(str, Enum):
    FOOD_DINING = "food_dining"
    SHOPPING = "shopping"
    ENTERTAINMENT = "entertainment"
    TRANSPORTATION = "transportation"
    BILLS_UTILITIES = "bills_utilities"
    HEALTHCARE = "healthcare"
    TRAVEL = "travel"
    INCOME = "income"
    TRANSFER = "transfer"
    OTHER = "other"

class GoalType(str, Enum):
    EMERGENCY_FUND = "emergency_fund"
    DEBT_PAYOFF = "debt_payoff"
    INVESTMENT = "investment"
    SAVINGS_TARGET = "savings_target"
    RETIREMENT = "retirement"
    VACATION = "vacation"
    HOME_PURCHASE = "home_purchase"

class BudgetPeriod(str, Enum):
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    YEARLY = "yearly"

# User Models
class User(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    email: str
    full_name: str
    phone: Optional[str] = None
    date_of_birth: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = True
    subscription_tier: str = "free"  # free, premium, pro
    financial_health_score: Optional[float] = None
    last_analysis_date: Optional[datetime] = None

class UserCreate(BaseModel):
    email: str
    full_name: str
    phone: Optional[str] = None
    date_of_birth: Optional[str] = None

# Account Models
class Account(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    plaid_account_id: Optional[str] = None
    plaid_item_id: Optional[str] = None
    institution_name: str
    account_name: str
    account_type: AccountType
    account_subtype: Optional[str] = None
    balance_current: float = 0.0
    balance_available: Optional[float] = None
    account_mask: Optional[str] = None
    currency_code: str = "USD"
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_sync: Optional[datetime] = None

class AccountCreate(BaseModel):
    institution_name: str
    account_name: str
    account_type: AccountType
    balance_current: float = 0.0
    balance_available: Optional[float] = None

class AccountUpdate(BaseModel):
    account_name: Optional[str] = None
    balance_current: Optional[float] = None
    balance_available: Optional[float] = None
    is_active: Optional[bool] = None

# Transaction Models
class Transaction(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    account_id: str
    plaid_transaction_id: Optional[str] = None
    amount: float
    currency_code: str = "USD"
    transaction_name: str
    merchant_name: Optional[str] = None
    category: TransactionCategory = TransactionCategory.OTHER
    subcategory: Optional[str] = None
    transaction_date: datetime
    authorized_date: Optional[datetime] = None
    is_pending: bool = False
    location: Optional[Dict[str, Any]] = None
    payment_meta: Optional[Dict[str, Any]] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # AI-enhanced fields
    ai_category_confidence: Optional[float] = None
    ai_insights: Optional[Dict[str, Any]] = None
    is_recurring: Optional[bool] = None
    recurring_frequency: Optional[str] = None

class TransactionCreate(BaseModel):
    account_id: str
    amount: float
    transaction_name: str
    merchant_name: Optional[str] = None
    category: Optional[TransactionCategory] = TransactionCategory.OTHER
    transaction_date: datetime
    is_pending: bool = False

class TransactionUpdate(BaseModel):
    transaction_name: Optional[str] = None
    category: Optional[TransactionCategory] = None
    merchant_name: Optional[str] = None

# Budget Models
class Budget(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    name: str
    period: BudgetPeriod = BudgetPeriod.MONTHLY
    total_budget: float
    start_date: datetime
    end_date: Optional[datetime] = None
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # AI-generated fields
    ai_recommended: bool = False
    ai_confidence: Optional[float] = None
    ai_reasoning: Optional[str] = None

class BudgetCategory(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    budget_id: str
    category: TransactionCategory
    allocated_amount: float
    spent_amount: float = 0.0
    remaining_amount: float = 0.0
    is_over_budget: bool = False
    percentage_used: float = 0.0
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class BudgetCreate(BaseModel):
    name: str
    period: BudgetPeriod = BudgetPeriod.MONTHLY
    total_budget: float
    start_date: datetime
    categories: List[Dict[str, float]]  # [{"category": "food_dining", "amount": 500}]

# Financial Goal Models
class FinancialGoal(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    name: str
    goal_type: GoalType
    target_amount: float
    current_amount: float = 0.0
    target_date: datetime
    priority: int = 1  # 1-5, 1 being highest priority
    is_completed: bool = False
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    
    # AI fields
    ai_probability_success: Optional[float] = None
    ai_recommended_monthly_contribution: Optional[float] = None
    ai_insights: Optional[str] = None

class GoalCreate(BaseModel):
    name: str
    goal_type: GoalType
    target_amount: float
    target_date: datetime
    priority: int = 1

class GoalUpdate(BaseModel):
    name: Optional[str] = None
    target_amount: Optional[float] = None
    target_date: Optional[datetime] = None
    current_amount: Optional[float] = None
    priority: Optional[int] = None
    is_active: Optional[bool] = None

# AI Insights Models
class AIInsight(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    insight_type: str  # spending_pattern, budget_recommendation, goal_advice, etc.
    title: str
    description: str
    importance: int = 1  # 1-5, 1 being most important
    action_items: List[str] = []
    potential_savings: Optional[float] = None
    confidence_score: float
    data_points: Optional[Dict[str, Any]] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    is_read: bool = False
    is_dismissed: bool = False

class AIInsightCreate(BaseModel):
    insight_type: str
    title: str
    description: str
    importance: int = 1
    action_items: List[str] = []
    potential_savings: Optional[float] = None
    confidence_score: float
    data_points: Optional[Dict[str, Any]] = None

# Financial Health Score Models
class FinancialHealthScore(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    overall_score: float  # 0-100
    spending_score: float  # How well they manage spending
    saving_score: float    # How well they save money
    debt_score: float      # How well they manage debt
    emergency_fund_score: float  # Emergency fund adequacy
    investment_score: float      # Investment diversification
    
    # Score components breakdown
    score_factors: Dict[str, Any] = {}
    recommendations: List[str] = []
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    calculated_at: datetime = Field(default_factory=datetime.utcnow)

# Plaid Integration Models
class PlaidItem(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    item_id: str
    access_token_encrypted: str
    institution_id: Optional[str] = None
    institution_name: Optional[str] = None
    status: str = "active"  # active, error, expired
    error_code: Optional[str] = None
    webhook_url: Optional[str] = None
    sync_cursor: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_successful_sync: Optional[datetime] = None

# Response Models
class AccountsResponse(BaseModel):
    accounts: List[Account]
    total_balance: float
    total_count: int

class TransactionsResponse(BaseModel):
    transactions: List[Transaction]
    total_count: int
    has_more: bool
    next_cursor: Optional[str] = None

class BudgetResponse(BaseModel):
    budget: Budget
    categories: List[BudgetCategory]
    total_spent: float
    remaining_budget: float
    days_remaining: int

class FinancialDashboard(BaseModel):
    user: User
    accounts_summary: AccountsResponse
    recent_transactions: List[Transaction]
    active_budgets: List[Budget]
    financial_goals: List[FinancialGoal]
    financial_health_score: Optional[FinancialHealthScore]
    ai_insights: List[AIInsight]
    monthly_spending_by_category: Dict[str, float]
    net_worth: float
    monthly_cash_flow: float
