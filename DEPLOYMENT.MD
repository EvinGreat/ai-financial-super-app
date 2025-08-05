# 🚀 Deployment Guide

## Quick Deploy (15 minutes)

### 1. Frontend (Vercel)
- Connect GitHub repo to Vercel
- Build command: `cd frontend && yarn build`
- Output directory: `frontend/build`

### 2. Backend (Railway)  
- Connect GitHub repo to Railway
- Start command: `cd backend && python server.py`
- Add environment variables from backend/.env

### 3. Database (MongoDB Atlas)
- Create free cluster
- Get connection string
- Update MONGO_URL in backend environment

### 4. Environment Variables
Backend (.env):
- OPENAI_API_KEY=your_openai_key
- PLAID_CLIENT_ID=your_plaid_client_id  
- PLAID_SECRET=your_plaid_secret
- MONGO_URL=your_mongodb_connection_string

Frontend (.env):
- REACT_APP_BACKEND_URL=your_railway_backend_url
