# Agent Flow Specification - Tutor GPT System

## Overview
This document outlines the complete flow of all 6 agents in the Tutor GPT system according to the plan and specifications.

## The 6 Agents

### 1. 🎯 **Orchestrator Agent**
**Role**: Master coordinator and flow manager
**Responsibilities**:
- Manages the overall learning journey
- Routes users between different agents
- Handles session state transitions
- Sends initial greeting (FIRST RUNNER)
- Coordinates handoffs between agents

**Expected Flow**:
```
User connects → Orchestrator sends greeting → Routes to Assessment
```

### 2. 📝 **Assessment Agent** 
**Role**: Learning style and knowledge assessment
**Responsibilities**:
- Conducts VARK learning style assessment (5-12 questions)
- Evaluates user responses to identify learning preferences
- Stores assessment results
- Provides learning style summary

**Expected Flow**:
```
Orchestrator handoff → Ask VARK questions → Analyze responses → Determine learning style → Handoff to Planning
```

### 3. 📚 **Planning Agent**
**Role**: Personalized study plan creation
**Responsibilities**:
- Creates customized study plans based on assessment results
- Generates topic sequences and learning paths
- Estimates time requirements
- Adapts to user's learning style

**Expected Flow**:
```
Assessment results → Create personalized plan → Present study roadmap → Handoff to Tutor
```

### 4. 👨‍🏫 **Tutor Agent**
**Role**: Lesson delivery and explanation
**Responsibilities**:
- Delivers lessons tailored to learning style
- Provides explanations and examples
- Uses RAG for dynamic content
- Integrates with Tavily for live examples

**Expected Flow**:
```
Study plan → Deliver lessons → Explain concepts → Provide examples → Handoff to Quiz when ready
```

### 5. 📋 **Quiz Agent**
**Role**: Knowledge testing and validation
**Responsibilities**:
- Generates quizzes based on lesson content
- Evaluates user responses
- Provides immediate feedback
- Determines mastery level

**Expected Flow**:
```
Lesson completion → Generate quiz → Evaluate answers → Provide feedback → Route back to Tutor or advance
```

### 6. 💬 **Feedback Agent**
**Role**: Progress tracking and motivation
**Responsibilities**:
- Tracks learning progress
- Provides motivational feedback
- Identifies learning gaps
- Suggests improvements

**Expected Flow**:
```
User requests feedback → Analyze progress → Provide insights → Suggest next steps
```

## Complete Agent Flow

```
1. User Registration/Login
   ↓
2. Orchestrator Agent (Initial Greeting)
   ↓
3. Assessment Agent (VARK Assessment)
   ↓
4. Planning Agent (Study Plan Creation)
   ↓
5. Tutor Agent (Lesson Delivery)
   ↓
6. Quiz Agent (Knowledge Testing)
   ↓
7. Feedback Agent (Progress Tracking)
   ↓
8. Loop back to Tutor for next lesson OR
   Complete learning path
```

## Session States

The system uses these session states to track progress:

- `GREETING` → Orchestrator handles initial contact
- `ASSESSING` → Assessment Agent conducts VARK evaluation
- `PLANNING` → Planning Agent creates study plan
- `TUTORING` → Tutor Agent delivers lessons
- `QUIZZING` → Quiz Agent tests knowledge
- `REMEDIATING` → Additional help when needed
- `COMPLETING` → Final assessment and completion

## Agent Communication

### WebSocket Messages
- **User Input**: `{"message": "user text", "type": "user_message"}`
- **Agent Response**: `{"text": "agent response", "agent": "agent_name", "type": "agent_message"}`
- **State Transition**: `{"next_state": "new_state", "action": "handoff_to_agent"}`

### Agent Handoffs
- Orchestrator → Assessment: `"start_assessment"`
- Assessment → Planning: `"assessment_complete"`
- Planning → Tutor: `"handoff_to_tutor"`
- Tutor → Quiz: `"generate_quiz"`
- Quiz → Tutor: `"continue_learning"`
- Any → Feedback: `"request_feedback"`

## Expected Test Results

### ✅ Working Scenarios
1. **Complete Flow**: User goes through all 6 agents successfully
2. **Agent Handoffs**: Smooth transitions between agents
3. **State Management**: Proper session state updates
4. **RAG Integration**: Dynamic content generation
5. **Assessment Flow**: VARK questions and analysis
6. **Lesson Delivery**: Personalized teaching based on learning style

### ❌ Error Scenarios
1. **Agent Not Responding**: Timeout or connection issues
2. **Incorrect Handoffs**: Agent doesn't route properly
3. **State Confusion**: Session state not updated correctly
4. **RAG Failures**: Content generation fails
5. **Assessment Issues**: Questions not generated or evaluated incorrectly

## Success Criteria

**Minimum Requirements**:
- All 6 agents respond to appropriate triggers
- WebSocket communication works reliably
- Session states update correctly
- Agent handoffs function properly
- RAG content generation works

**Optimal Performance**:
- Smooth user experience from greeting to completion
- Personalized content based on learning style
- Intelligent routing between agents
- Comprehensive progress tracking
- Real-time feedback and adaptation
