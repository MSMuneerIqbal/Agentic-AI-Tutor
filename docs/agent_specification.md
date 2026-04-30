# AI Agent Flow Specification

## Overview
The Tutor GPT AI agent system should provide a comprehensive, personalized learning experience with proper flow management, user assessment, and intelligent interactions.

## Agent Flow Requirements

### 1. Initial Greeting & Assessment
- **Welcome Message**: Personalized greeting with learning goals assessment
- **Learning Style Detection**: VARK (Visual, Auditory, Reading/Writing, Kinesthetic) assessment
- **Experience Level**: Beginner, Intermediate, Advanced detection
- **Learning Goals**: Docker, Kubernetes, DevOps, or specific topics

### 2. Session Management
- **Session Persistence**: Store all chat history in MongoDB
- **User Context**: Maintain user profile, progress, and preferences
- **Conversation State**: Track current topic, difficulty level, and learning objectives

### 3. Agent Types & Roles

#### Orchestrator Agent
- **Role**: Main coordinator, manages conversation flow
- **Responsibilities**: 
  - Route user messages to appropriate specialized agents
  - Maintain conversation context and user state
  - Handle greetings and general questions

#### Assessment Agent
- **Role**: Evaluate user knowledge and learning style
- **Responsibilities**:
  - Conduct VARK learning style assessment
  - Assess current Docker/Kubernetes knowledge level
  - Recommend learning path based on assessment

#### Tutor Agent
- **Role**: Provide educational content and explanations
- **Responsibilities**:
  - Deliver personalized lessons based on user's learning style
  - Provide detailed explanations with examples
  - Adapt content complexity to user level

#### Quiz Agent
- **Role**: Generate and manage assessments
- **Responsibilities**:
  - Create dynamic quizzes based on learned material
  - Provide immediate feedback and explanations
  - Track learning progress and gaps

#### Feedback Agent
- **Role**: Monitor progress and provide encouragement
- **Responsibilities**:
  - Analyze learning patterns and progress
  - Provide motivational feedback
  - Suggest improvements and next steps

### 4. Conversation Flow States

#### State 1: Initial Assessment (First Time Users)
1. Welcome message with learning goals
2. VARK learning style questions (3-5 questions)
3. Experience level assessment
4. Topic preference selection
5. Create personalized learning plan

#### State 2: Learning Mode (Returning Users)
1. Quick progress check
2. Continue from last topic or new topic
3. Adaptive content delivery
4. Progress tracking and feedback

#### State 3: Interactive Learning
1. Topic explanation with examples
2. Hands-on exercises or demonstrations
3. Quiz or practice questions
4. Feedback and next steps

### 5. Response Types

#### Greeting Responses
- Personalized welcome based on user data
- Progress acknowledgment for returning users
- Learning path recommendations

#### Educational Responses
- Concept explanations with analogies
- Step-by-step tutorials
- Code examples and demonstrations
- Real-world use cases

#### Assessment Responses
- Learning style questions
- Knowledge level evaluation
- Progress check-ins
- Feedback and recommendations

#### Interactive Responses
- Follow-up questions
- Clarification requests
- Exercise prompts
- Quiz questions

### 6. Data Storage Requirements

#### User Profile
- Learning style (VARK)
- Experience level
- Learning goals
- Progress tracking
- Preferred topics

#### Session Data
- Chat history
- Current topic
- Learning state
- Progress metrics
- Interaction patterns

#### Learning Progress
- Completed topics
- Quiz scores
- Time spent learning
- Difficulty progression
- Achievements

## Implementation Requirements

### Backend Components
1. **Agent Manager**: Route messages to appropriate agents
2. **Session Store**: MongoDB-based session management
3. **User Profile Service**: Manage user preferences and progress
4. **Assessment Engine**: Conduct and store assessments
5. **Learning Path Generator**: Create personalized curricula

### Frontend Components
1. **Chat Interface**: Real-time conversation display
2. **Progress Tracker**: Visual progress indicators
3. **Assessment Forms**: VARK and experience level forms
4. **Learning Dashboard**: Overview of progress and achievements

### Integration Points
1. **MongoDB**: User profiles, sessions, progress data
2. **WebSocket**: Real-time agent communication
3. **Assessment APIs**: Learning style and progress evaluation
4. **Content APIs**: Educational material delivery
