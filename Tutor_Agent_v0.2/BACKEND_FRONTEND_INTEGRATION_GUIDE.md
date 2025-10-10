# 🔗 Backend-Frontend Integration Guide

## 📋 **OVERVIEW**

This guide provides complete instructions for connecting and running your Tutor GPT backend and frontend together as a unified system.

---

## 🚀 **QUICK START**

### **Option 1: Automated Startup (Recommended)**
```bash
# Run the complete system startup script
python start_complete_system.py
```

### **Option 2: Manual Startup**
```bash
# Terminal 1: Start Backend
cd backend
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Terminal 2: Start Frontend
cd frontend
npm install  # First time only
npm run dev
```

---

## 🔧 **SYSTEM REQUIREMENTS**

### **Backend Requirements**
- Python 3.12+
- uv package manager
- MySQL database
- Redis server
- Environment variables configured

### **Frontend Requirements**
- Node.js 18+
- npm or yarn
- Modern web browser

---

## 📁 **PROJECT STRUCTURE**

```
Tutor_Agent_v0.2/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── agents/         # AI agents
│   │   ├── api/           # API routes
│   │   ├── core/          # Configuration
│   │   ├── models/        # Database models
│   │   ├── services/      # Business logic
│   │   └── main.py        # FastAPI app
│   ├── .env               # Environment variables
│   └── requirements.txt   # Python dependencies
├── frontend/              # Next.js frontend
│   ├── src/
│   │   ├── app/          # Next.js app router
│   │   ├── components/   # React components
│   │   └── lib/          # Utilities
│   ├── package.json      # Node dependencies
│   └── .env.local        # Frontend environment
└── scripts/              # Integration scripts
    ├── start_complete_system.py
    ├── test_complete_system.py
    ├── test_integration.py
    └── quick_test.py
```

---

## 🌐 **SERVICE ENDPOINTS**

### **Backend Services**
- **API Server**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/healthz
- **WebSocket**: ws://localhost:8000/ws
- **Metrics**: http://localhost:8000/api/v1/metrics

### **Frontend Services**
- **Web Application**: http://localhost:3000
- **Development Server**: http://localhost:3000 (with hot reload)

---

## 🔌 **INTEGRATION POINTS**

### **1. API Communication**
```typescript
// Frontend API client configuration
const API_BASE_URL = 'http://localhost:8000'

// Example API call
const response = await fetch(`${API_BASE_URL}/api/v1/chat`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ user_input: 'Hello' })
})
```

### **2. WebSocket Communication**
```typescript
// Frontend WebSocket connection
const ws = new WebSocket('ws://localhost:8000/ws')

ws.onmessage = (event) => {
  const data = JSON.parse(event.data)
  // Handle agent messages
}
```

### **3. Authentication Flow**
```typescript
// Frontend authentication
const loginResponse = await fetch(`${API_BASE_URL}/api/v1/auth/login`, {
  method: 'POST',
  body: JSON.stringify({ email, password })
})

const { user, token } = await loginResponse.json()
localStorage.setItem('tutor-gpt-user', JSON.stringify(user))
```

---

## 🧪 **TESTING INTEGRATION**

### **Quick Connection Test**
```bash
python quick_test.py
```

### **Complete Integration Test**
```bash
python test_integration.py
```

### **Full System Test**
```bash
python test_complete_system.py
```

---

## 🔧 **CONFIGURATION**

### **Backend Environment (.env)**
```env
# Database
DATABASE_URL=mysql+aiomysql://user:password@localhost:3306/tutor_gpt

# Redis
REDIS_URL=redis://localhost:6379

# API Keys
GEMINI_API_KEY=your_gemini_key
TAVILY_API_KEY=your_tavily_key
PINECONE_API_KEY=your_pinecone_key

# Security
SECRET_KEY=your_secret_key
```

### **Frontend Environment (.env.local)**
```env
# API Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000

# App Configuration
NEXT_PUBLIC_APP_NAME=Tutor GPT
NEXT_PUBLIC_APP_VERSION=2.0.0
```

---

## 🚀 **DEPLOYMENT OPTIONS**

### **Development Mode**
- Backend: `uvicorn app.main:app --reload`
- Frontend: `npm run dev`
- Hot reload enabled for both

### **Production Mode**
- Backend: `uvicorn app.main:app --host 0.0.0.0 --port 8000`
- Frontend: `npm run build && npm start`
- Optimized builds

### **Docker Deployment**
```bash
# Build and run with Docker Compose
docker-compose up --build
```

---

## 🔍 **TROUBLESHOOTING**

### **Common Issues**

#### **Backend Not Starting**
```bash
# Check Python version
python --version  # Should be 3.12+

# Install dependencies
cd backend
uv sync

# Check environment variables
cat .env

# Start with debug
uv run uvicorn app.main:app --reload --log-level debug
```

#### **Frontend Not Starting**
```bash
# Check Node version
node --version  # Should be 18+

# Install dependencies
cd frontend
npm install

# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install

# Start with debug
npm run dev -- --verbose
```

#### **API Connection Issues**
```bash
# Test backend health
curl http://localhost:8000/healthz

# Test API endpoints
curl http://localhost:8000/api/v1/health

# Check CORS settings in backend
```

#### **WebSocket Connection Issues**
```bash
# Test WebSocket connection
wscat -c ws://localhost:8000/ws

# Check WebSocket logs in backend
# Verify WebSocket middleware is enabled
```

---

## 📊 **MONITORING & LOGS**

### **Backend Logs**
```bash
# View backend logs
tail -f backend/logs/app.log

# Monitor API requests
curl http://localhost:8000/api/v1/metrics
```

### **Frontend Logs**
```bash
# View browser console
# Check Network tab for API calls
# Monitor WebSocket connections
```

### **System Health**
```bash
# Check all services
python quick_test.py

# Detailed system test
python test_complete_system.py
```

---

## 🔄 **DEVELOPMENT WORKFLOW**

### **1. Start Development**
```bash
# Start both services
python start_complete_system.py
```

### **2. Make Changes**
- Backend changes: Auto-reload with uvicorn --reload
- Frontend changes: Hot reload with Next.js
- Database changes: Restart backend

### **3. Test Changes**
```bash
# Quick test
python quick_test.py

# Full integration test
python test_integration.py
```

### **4. Deploy**
```bash
# Build for production
cd frontend && npm run build
cd backend && uv run uvicorn app.main:app --host 0.0.0.0
```

---

## 🎯 **INTEGRATION FEATURES**

### **Real-time Communication**
- ✅ WebSocket connection between frontend and backend
- ✅ Real-time chat with AI agents
- ✅ Live session updates
- ✅ Agent handoff notifications

### **API Integration**
- ✅ Authentication endpoints
- ✅ User management
- ✅ Learning progress tracking
- ✅ RAG content retrieval
- ✅ Assessment and quiz APIs

### **Data Synchronization**
- ✅ User session management
- ✅ Learning progress sync
- ✅ Real-time analytics
- ✅ Collaborative features

---

## 📈 **PERFORMANCE OPTIMIZATION**

### **Backend Optimization**
- Database connection pooling
- Redis caching
- API response compression
- WebSocket connection management

### **Frontend Optimization**
- Code splitting and lazy loading
- Image optimization
- API response caching
- WebSocket reconnection logic

---

## 🔐 **SECURITY CONSIDERATIONS**

### **API Security**
- JWT token authentication
- CORS configuration
- Rate limiting
- Input validation

### **WebSocket Security**
- Connection authentication
- Message validation
- Rate limiting
- Secure WebSocket (WSS) in production

---

## 🎉 **SUCCESS INDICATORS**

### **System is Working When:**
- ✅ Backend health check returns 200
- ✅ Frontend loads without errors
- ✅ WebSocket connection established
- ✅ API endpoints respond correctly
- ✅ AI agents can communicate
- ✅ User authentication works
- ✅ Real-time chat functions

### **Integration Test Results:**
- ✅ 80%+ test success rate = HEALTHY
- ✅ 60-79% test success rate = DEGRADED
- ✅ <60% test success rate = UNHEALTHY

---

## 📞 **SUPPORT**

### **Getting Help**
1. Check the troubleshooting section above
2. Run the integration tests to identify issues
3. Check logs for error messages
4. Verify environment configuration

### **Common Commands**
```bash
# Start system
python start_complete_system.py

# Test connection
python quick_test.py

# Full test
python test_complete_system.py

# Check logs
tail -f backend/logs/app.log
```

---

**🎯 Your Tutor GPT system is now ready for complete backend-frontend integration!**

**Next Steps:**
1. Run `python start_complete_system.py` to start both services
2. Open http://localhost:3000 in your browser
3. Test the complete system with real user interactions
4. Deploy to production when ready
