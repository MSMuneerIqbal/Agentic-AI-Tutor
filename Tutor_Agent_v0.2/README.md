# 🤖 Tutor GPT - AI-Powered Learning Platform

![Tutor GPT Logo](https://img.shields.io/badge/Tutor%20GPT-AI%20Learning-blue?style=for-the-badge&logo=robot)
![Status](https://img.shields.io/badge/Status-Production%20Ready-green?style=for-the-badge)
![Agents](https://img.shields.io/badge/Agents-6%20AI%20Agents-orange?style=for-the-badge)

## 📋 Table of Contents

- [🎯 Overview](#-overview)
- [🚀 Features](#-features)
- [🤖 AI Agents](#-ai-agents)
- [🏗️ Architecture](#️-architecture)
- [📁 Project Structure](#-project-structure)
- [⚙️ Installation](#️-installation)
- [🔧 Configuration](#-configuration)
- [🚀 Usage](#-usage)
- [📊 API Endpoints](#-api-endpoints)
- [🧪 Testing](#-testing)
- [📈 Specifications](#-specifications)
- [🎯 Development Plans](#-development-plans)
- [🤝 Contributing](#-contributing)
- [📄 License](#-license)

## 🎯 Overview

Tutor GPT is an advanced AI-powered learning platform specializing in Docker and Kubernetes education. The system uses 6 specialized AI agents to provide personalized, adaptive learning experiences with real-time content retrieval and live examples.

### Key Highlights
- ✅ **6 AI Agents** working in harmony
- ✅ **Real RAG Content** from Pinecone vector database
- ✅ **Live Examples** from Tavily MCP integration
- ✅ **Personalized Learning** with VARK assessment
- ✅ **WebSocket Communication** for real-time interaction
- ✅ **MongoDB Integration** for persistent sessions
- ✅ **Production Ready** with comprehensive error handling

## 🚀 Features

### 🎓 Learning Features
- **Adaptive Learning Paths** - Personalized based on learning style assessment
- **Real-time Content Retrieval** - Live examples and current best practices
- **Interactive Assessments** - VARK learning style detection
- **Progress Tracking** - Comprehensive analytics and feedback
- **Session Persistence** - Resume learning across sessions
- **Multi-modal Learning** - Visual, Auditory, Reading, Kinesthetic support

### 🤖 AI-Powered Features
- **Intelligent Agent Routing** - Smart conversation flow management
- **Context-Aware Responses** - Maintains conversation history
- **Dynamic Content Generation** - Real-time lesson and quiz creation
- **Personalized Feedback** - Adaptive based on performance
- **Topic Skipping Logic** - Intelligent assessment for advanced learners
- **Real-time Analytics** - Learning pattern analysis

### 🔧 Technical Features
- **FastAPI Backend** - High-performance async API
- **Next.js Frontend** - Modern React-based UI
- **WebSocket Communication** - Real-time agent interaction
- **MongoDB Storage** - Scalable document-based persistence
- **RAG Integration** - Vector-based content retrieval
- **External API Integration** - Tavily for live examples

## 🤖 AI Agents

### 1. 🎭 Orchestrator Agent
**Purpose**: Master coordinator managing the entire learning flow
- **Responsibilities**:
  - Route user requests to appropriate agents
  - Manage session state transitions
  - Handle agent handoffs and context preservation
  - Provide initial greetings and flow guidance
  - Coordinate topic skipping assessments
- **Specialties**: Flow management, agent coordination, session orchestration

### 2. 📊 Assessment Agent
**Purpose**: Learning style detection and skill evaluation
- **Responsibilities**:
  - VARK learning style assessment
  - Experience level evaluation
  - Learning preference analysis
  - Adaptive questioning strategies
- **Specialties**: Learning psychology, assessment design, personalization

### 3. 👨‍🏫 Tutor Agent
**Purpose**: Primary educator delivering personalized lessons
- **Responsibilities**:
  - Deliver lessons adapted to learning style
  - Integrate RAG content from knowledge base
  - Provide live examples from Tavily
  - Offer hands-on exercises and practice
  - Handle topic skipping guidance
- **Specialties**: Content delivery, RAG integration, adaptive teaching

### 4. 📝 Quiz Agent
**Purpose**: Knowledge testing and validation
- **Responsibilities**:
  - Generate dynamic quiz questions
  - Adaptive difficulty adjustment
  - Real-time scoring and feedback
  - Topic-specific assessments
  - Progress validation
- **Specialties**: Assessment design, adaptive testing, performance evaluation

### 5. 💬 Feedback Agent
**Purpose**: Progress analysis and improvement guidance
- **Responsibilities**:
  - Analyze learning patterns and progress
  - Provide personalized feedback
  - Identify learning gaps
  - Suggest improvement strategies
  - Track long-term progress
- **Specialties**: Analytics, progress tracking, improvement recommendations

### 6. 📋 Planning Agent
**Purpose**: Study plan creation and goal management
- **Responsibilities**:
  - Create personalized study plans
  - Set learning objectives and milestones
  - Track goal progress
  - Adjust plans based on performance
  - Coordinate with other agents
- **Specialties**: Curriculum design, goal setting, progress planning

## 🏗️ Architecture

### System Architecture
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend       │    │   External      │
│   (Next.js)     │◄──►│   (FastAPI)     │◄──►│   Services      │
│                 │    │                 │    │                 │
│ • React UI      │    │ • 6 AI Agents   │    │ • Pinecone      │
│ • WebSocket     │    │ • WebSocket     │    │ • Tavily        │
│ • Auth System   │    │ • Session Mgmt  │    │ • Gemini        │
│ • Dashboard     │    │ • API Endpoints │    │ • MongoDB       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Agent Flow
```
Student Input → WebSocket → AgentManager → Orchestrator
                                      ↓
                    ┌─────────────────┴─────────────────┐
                    ↓                 ↓                 ↓
              Assessment          Tutor              Quiz
                    ↓                 ↓                 ↓
                    └─────────────────┬─────────────────┘
                                      ↓
                            Feedback & Planning
```

### Data Flow
1. **User Authentication** → MongoDB User Storage
2. **Session Creation** → MongoDB Session Management
3. **Agent Interaction** → WebSocket Real-time Communication
4. **Content Retrieval** → Pinecone RAG + Tavily Live Examples
5. **AI Processing** → Gemini Model Integration
6. **Progress Tracking** → MongoDB Analytics Storage

## 📁 Project Structure

```
Tutor_Agent_v0.2/
├── 📁 backend/                          # FastAPI Backend
│   ├── 📁 app/
│   │   ├── 📁 agents/                   # AI Agent Implementations
│   │   │   ├── orchestrator.py         # Master coordinator
│   │   │   ├── assessment.py           # Learning assessment
│   │   │   ├── tutor.py                # Primary educator
│   │   │   ├── quiz.py                 # Knowledge testing
│   │   │   ├── feedback.py             # Progress analysis
│   │   │   ├── planning.py             # Study planning
│   │   │   └── agent_manager.py        # Agent coordination
│   │   ├── 📁 api/routes/              # API Endpoints
│   │   │   ├── auth.py                 # Authentication
│   │   │   ├── sessions.py             # Session management
│   │   │   ├── websocket.py            # Real-time communication
│   │   │   ├── profiles.py             # User profiles
│   │   │   ├── assessments.py          # Assessment data
│   │   │   └── plans.py                # Study plans
│   │   ├── 📁 core/                    # Core functionality
│   │   │   ├── config.py               # Configuration
│   │   │   ├── database.py             # Database setup
│   │   │   ├── mongodb.py              # MongoDB connection
│   │   │   ├── session_store.py        # Session management
│   │   │   └── logging.py              # Logging system
│   │   ├── 📁 models/                  # Data models
│   │   │   ├── user_mongo.py           # User model
│   │   │   ├── session.py              # Session model
│   │   │   └── assessment.py           # Assessment model
│   │   ├── 📁 services/                # Business logic
│   │   │   ├── rag_service.py          # RAG integration
│   │   │   ├── profile_service.py      # Profile management
│   │   │   └── plan_service.py         # Plan management
│   │   ├── 📁 tools/                   # External integrations
│   │   │   ├── rag.py                  # Pinecone integration
│   │   │   └── tavily_mcp.py           # Tavily integration
│   │   └── main.py                     # FastAPI application
│   ├── 📄 .env                         # Environment variables
│   └── 📄 pyproject.toml               # Python dependencies
├── 📁 frontend/                         # Next.js Frontend
│   ├── 📁 src/
│   │   ├── 📁 app/                     # App router pages
│   │   │   ├── page.tsx                # Landing page
│   │   │   ├── dashboard/page.tsx      # Dashboard page
│   │   │   └── layout.tsx              # Root layout
│   │   ├── 📁 components/              # React components
│   │   │   ├── 📁 auth/                # Authentication
│   │   │   ├── 📁 chat/                # Chat interface
│   │   │   ├── 📁 dashboard/           # Dashboard components
│   │   │   └── 📁 landing/             # Landing page
│   │   └── 📁 providers.tsx            # Context providers
│   ├── 📄 package.json                 # Node dependencies
│   └── 📄 next.config.js               # Next.js configuration
├── 📄 test_real_agents.py              # Agent testing script
├── 📄 REAL_AGENT_SETUP.md              # Setup instructions
├── 📄 AGENTS_STATUS_FINAL.md           # Agent status report
└── 📄 README.md                        # This file
```

## ⚙️ Installation

### Prerequisites
- **Python 3.12+**
- **Node.js 18+**
- **MongoDB Atlas Account**
- **API Keys**: Pinecone, Tavily, Gemini

### Backend Setup
```bash
# Clone the repository
git clone <repository-url>
cd Tutor_Agent_v0.2

# Navigate to backend
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
# Edit .env with your API keys
```

### Frontend Setup
```bash
# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Configure environment (if needed)
cp .env.example .env.local
```

## 🔧 Configuration

### Environment Variables (`backend/.env`)
```bash
# API Keys (Required)
GEMINI_API_KEY=your_gemini_api_key
TAVILY_API_KEY=your_tavily_api_key
PINECONE_API_KEY=your_pinecone_api_key

# MongoDB
MONGODB_URL=mongodb+srv://username:password@cluster.mongodb.net/database

# Application
ENVIRONMENT=development
DEBUG=true
```

### API Key Setup
1. **Gemini API**: Get from [Google AI Studio](https://aistudio.google.com/)
2. **Tavily API**: Get from [Tavily Dashboard](https://tavily.com/)
3. **Pinecone API**: Get from [Pinecone Console](https://app.pinecone.io/)
4. **MongoDB**: Use provided connection string

## 🚀 Usage

### Development Mode

#### Start Backend
```bash
cd backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### Start Frontend
```bash
cd frontend
npm run dev
```

#### Access Application
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

### Production Mode

#### Build Frontend
```bash
cd frontend
npm run build
npm start
```

#### Deploy Backend
```bash
cd backend
pip install gunicorn
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker
```

### Using the Application

#### 1. Student Registration
1. Visit the landing page
2. Click "Sign Up"
3. Provide email and password
4. Complete registration

#### 2. Learning Journey
1. **Login** to your account
2. **Assessment** - Complete learning style evaluation
3. **Planning** - Get personalized study plan
4. **Learning** - Interact with AI Tutor
5. **Testing** - Take quizzes and assessments
6. **Feedback** - Receive progress analysis

#### 3. Agent Interaction
- **Chat Interface** - Real-time conversation with AI agents
- **Dashboard** - View progress and statistics
- **WebSocket** - Seamless agent communication

## 📊 API Endpoints

### Authentication
- `POST /api/v1/auth/register` - User registration
- `POST /api/v1/auth/login` - User login

### Sessions
- `POST /api/v1/sessions/start` - Start new session
- `GET /api/v1/sessions/{session_id}` - Get session details

### Profiles
- `GET /api/v1/profiles/{user_id}` - Get user profile
- `PUT /api/v1/profiles/{user_id}` - Update user profile
- `GET /api/v1/profiles/{user_id}/assessments` - Get assessment history

### Plans
- `GET /api/v1/plans/{user_id}` - Get user study plans
- `POST /api/v1/plans/{user_id}` - Create new study plan
- `GET /api/v1/plans/{user_id}/latest` - Get latest plan

### WebSocket
- `WS /ws/sessions/{session_id}` - Real-time agent communication

### Assessments
- `GET /api/v1/assessments/` - List available assessments
- `POST /api/v1/assessments/submit` - Submit assessment results

### RAG & Content
- `GET /api/v1/rag/search` - Search knowledge base
- `GET /api/v1/rag/topic/{topic}` - Get topic content

### Metrics
- `GET /metrics` - Application metrics

## 🧪 Testing

### Test All Agents
```bash
python test_real_agents.py
```

### Test Individual Components
```bash
# Test backend
cd backend
pytest

# Test frontend
cd frontend
npm test
```

### Test WebSocket Connection
```bash
python test_websocket_connection.py
```

### Test Database
```bash
python test_mongodb_connection.py
```

## 📈 Specifications

### Technical Specifications
- **Backend**: FastAPI (Python 3.12+)
- **Frontend**: Next.js 14 (React 18+)
- **Database**: MongoDB Atlas
- **AI Models**: Gemini 1.5 Pro
- **Vector DB**: Pinecone
- **Live Examples**: Tavily MCP
- **Communication**: WebSocket
- **Authentication**: Session-based

### Performance Specifications
- **Response Time**: < 2 seconds for agent responses
- **Concurrent Users**: 100+ simultaneous sessions
- **Uptime**: 99.9% availability target
- **Scalability**: Horizontal scaling support

### Security Specifications
- **Authentication**: Secure session management
- **Data Protection**: Encrypted data transmission
- **API Security**: Rate limiting and validation
- **Privacy**: GDPR-compliant data handling

## 🎯 Development Plans

### Phase 1: Core Foundation ✅
- [x] 6 AI Agent implementation
- [x] WebSocket communication
- [x] MongoDB integration
- [x] Authentication system
- [x] Basic frontend interface

### Phase 2: Advanced Features ✅
- [x] RAG content integration
- [x] Tavily live examples
- [x] Session persistence
- [x] Progress tracking
- [x] Assessment system

### Phase 3: Production Ready ✅
- [x] Error handling
- [x] Logging system
- [x] API documentation
- [x] Testing framework
- [x] Deployment configuration

### Phase 4: Future Enhancements 🚧
- [ ] Mobile app development
- [ ] Advanced analytics dashboard
- [ ] Multi-language support
- [ ] Collaborative learning features
- [ ] AI model fine-tuning
- [ ] Enterprise features

### Phase 5: Scale & Optimize 🚧
- [ ] Microservices architecture
- [ ] Advanced caching strategies
- [ ] Load balancing
- [ ] CDN integration
- [ ] Performance optimization

## 🤝 Contributing

### Development Workflow
1. **Fork** the repository
2. **Create** feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** changes (`git commit -m 'Add amazing feature'`)
4. **Push** to branch (`git push origin feature/amazing-feature`)
5. **Open** Pull Request

### Code Standards
- **Python**: PEP 8 compliance, type hints required
- **JavaScript**: ESLint configuration, TypeScript preferred
- **Documentation**: Comprehensive docstrings and comments
- **Testing**: Unit tests for all new features

### Agent Development
- Follow agent architecture patterns
- Implement proper error handling
- Add comprehensive logging
- Include unit tests
- Update documentation

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

### Documentation
- [Agent Architecture Guide](AGENTS_STATUS_FINAL.md)
- [Setup Instructions](REAL_AGENT_SETUP.md)
- [API Documentation](http://localhost:8000/docs)

### Getting Help
- **Issues**: Create GitHub issue for bugs
- **Discussions**: Use GitHub Discussions for questions
- **Email**: Contact project maintainers

### Troubleshooting
- Check API key configuration
- Verify MongoDB connection
- Review application logs
- Test individual components

---

## 🎉 Success Metrics

### Agent Performance
- ✅ **6 Agents** fully integrated and functional
- ✅ **Real-time Communication** via WebSocket
- ✅ **Session Persistence** across reconnects
- ✅ **Content Integration** with RAG and Tavily
- ✅ **Personalized Learning** with VARK assessment

### System Reliability
- ✅ **Error Handling** with graceful fallbacks
- ✅ **Logging System** for debugging and monitoring
- ✅ **Database Integration** with MongoDB Atlas
- ✅ **API Documentation** with OpenAPI/Swagger
- ✅ **Testing Framework** for quality assurance

### User Experience
- ✅ **Intuitive Interface** with modern React UI
- ✅ **Real-time Interaction** with AI agents
- ✅ **Progress Tracking** and analytics
- ✅ **Responsive Design** for all devices
- ✅ **Fast Performance** with optimized responses

---

**🚀 Tutor GPT is ready for production use with all 6 AI agents working together to provide the ultimate personalized learning experience!**