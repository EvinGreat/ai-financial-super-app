from fastapi import FastAPI, APIRouter, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
import logging
from datetime import datetime
from typing import List, Optional

# Load environment variables
load_dotenv()

# Simple in-memory storage for demo
users_db = []

# Create the main app
app = FastAPI(
    title="AI Financial Super-App",
    description="Billion-dollar AI-powered personal finance platform",
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
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "message": "Backend is running successfully"
    }

@api_router.post("/users")
async def create_user(user_data: dict):
    """Create a new user."""
    try:
        # Create simple user object
        new_user = {
            "id": str(len(users_db) + 1),
            "email": user_data.get("email"),
            "full_name": user_data.get("full_name"),
            "phone": user_data.get("phone", ""),
            "created_at": datetime.utcnow().isoformat(),
            "subscription_tier": "free"
        }
        
        # Add to our simple database
        users_db.append(new_user)
        
        logger.info(f"Created new user: {new_user['id']}")
        return new_user
        
    except Exception as e:
        logger.error(f"Error creating user: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create user")

# Include the router in the main app
app.include_router(api_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
