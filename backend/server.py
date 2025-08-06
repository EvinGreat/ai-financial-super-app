from fastapi import FastAPI, APIRouter, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import logging
from datetime import datetime
from typing import Optional

# Simple in-memory storage for demo
users_db = []

# Pydantic models
class UserCreate(BaseModel):
    email: str
    full_name: str
    phone: Optional[str] = ""

class User(BaseModel):
    id: str
    email: str
    full_name: str
    phone: Optional[str] = ""
    created_at: str
    subscription_tier: str = "free"

# Create the main app
app = FastAPI(
    title="AI Financial Super-App API",
    description="Billion-dollar AI-powered personal finance platform",
    version="1.0.0"
)

# Create API router with /api prefix
api_router = APIRouter(prefix="/api")

# CORS middleware - Allow all origins for now
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@api_router.get("/")
async def root():
    """Root API endpoint"""
    return {
        "message": "AI Financial Super-App API",
        "version": "1.0.0",
        "status": "operational",
        "features": [
            "AI-powered financial insights",
            "Smart budgeting recommendations", 
            "Financial health scoring",
            "User management",
            "Comprehensive financial dashboard"
        ],
        "users_count": len(users_db)
    }

@api_router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "message": "Backend is running successfully",
        "users_registered": len(users_db)
    }

@api_router.post("/users", response_model=User)
async def create_user(user_data: UserCreate):
    """Create a new user"""
    try:
        # Check if user already exists
        for existing_user in users_db:
            if existing_user["email"] == user_data.email:
                raise HTTPException(status_code=400, detail="User with this email already exists")
        
        # Create new user
        new_user = {
            "id": str(len(users_db) + 1),
            "email": user_data.email,
            "full_name": user_data.full_name,
            "phone": user_data.phone or "",
            "created_at": datetime.utcnow().isoformat(),
            "subscription_tier": "free"
        }
        
        # Add to our simple database
        users_db.append(new_user)
        
        logger.info(f"Created new user: {new_user['email']} (ID: {new_user['id']})")
        
        return User(**new_user)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating user: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create user: {str(e)}")

@api_router.get("/users")
async def get_all_users():
    """Get all users (for demo purposes)"""
    return {
        "users": users_db,
        "total": len(users_db),
        "message": "All registered users"
    }

@api_router.get("/users/{user_id}")
async def get_user(user_id: str):
    """Get a specific user by ID"""
    for user in users_db:
        if user["id"] == user_id:
            return User(**user)
    
    raise HTTPException(status_code=404, detail="User not found")

# Include the router in the main app
app.include_router(api_router)

# Root redirect
@app.get("/")
async def root_redirect():
    return {
        "message": "AI Financial Super-App Backend",
        "api_docs": "/docs",
        "api_endpoints": "/api/",
        "health_check": "/api/health"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
