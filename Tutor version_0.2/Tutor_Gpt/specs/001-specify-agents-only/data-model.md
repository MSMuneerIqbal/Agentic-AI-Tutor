# Data Model: Agent Layer Implementation

## Entity: Student Profile
- **Fields**: 
  - student_id (UUID, primary key)
  - name (string, required)
  - email (string, unique, nullable for anonymous users)
  - knowledge_level (enum: beginner, intermediate, advanced)
  - learning_preferences (JSON, e.g., {visual: true, auditory: false, kinesthetic: true})
  - assessment_results (JSON, stored assessment data)
  - created_at (timestamp)
  - updated_at (timestamp)
  - last_activity_at (timestamp, for retention policy)
  - deleted_at (timestamp, nullable, for soft deletion)
- **Relationships**: One-to-many with Quiz Results, One Study Plan
- **Validation**: Name required, knowledge_level must be valid enum value, FERPA/COPPA compliance for minors
- **State transitions**: Created during assessment → Updated during tutoring → Soft deleted after 1 year of inactivity → Hard deleted in background job

## Entity: Study Plan
- **Fields**: 
  - plan_id (UUID, primary key)
  - student_id (foreign key, references Student Profile)
  - topics (array of strings)
  - goals (array of strings)
  - created_at (timestamp)
  - updated_at (timestamp)
- **Relationships**: Belongs to Student Profile, contains many Lesson Plans
- **Validation**: Must have at least one topic, student_id must reference existing student
- **State transitions**: Created during planning → Updated as student progresses → Completed when goals met

## Entity: Lesson Content
- **Fields**: 
  - lesson_id (UUID, primary key)
  - topic (string)
  - intro (text)
  - explanation (text)
  - example (text)
  - exercise (text)
  - created_at (timestamp)
  - updated_at (timestamp)
  - tavily_results (JSON, cached results from Tavily)
- **Relationships**: Belongs to Study Plan
- **Validation**: All content fields required, topic must match plan's topics
- **State transitions**: Created on demand or retrieved from repository

## Entity: Quiz Result
- **Fields**: 
  - result_id (UUID, primary key)
  - student_id (foreign key, references Student Profile)
  - score (decimal, 0.0 to 1.0)
  - questions_count (integer)
  - weak_topics (array of strings)
  - hints_used (integer)
  - quiz_date (timestamp)
  - created_at (timestamp)
  - updated_at (timestamp)
- **Relationships**: Belongs to Student Profile
- **Validation**: Score between 0 and 1, questions_count must be positive
- **State transitions**: Created when quiz completed → May be updated with remediation results

## Entity: Teaching Directive
- **Fields**: 
  - directive_id (UUID, primary key)
  - student_id (foreign key, references Student Profile)
  - directive_type (enum: content_modification, pacing_adjustment, difficulty_change)
  - directive_text (text)
  - priority (enum: low, medium, high)
  - created_at (timestamp)
  - updated_at (timestamp)
- **Relationships**: Belongs to Student Profile
- **Validation**: Must reference valid student, priority must be valid enum
- **State transitions**: Created during feedback → Applied during tutoring → May be updated based on effectiveness

## Entity: Session Log
- **Fields**:
  - log_id (UUID, primary key)
  - student_id (foreign key, references Student Profile)
  - session_id (UUID)
  - agent_type (enum: assessment, planning, tutor, quiz, feedback)
  - action (string)
  - input (text, sanitized)
  - output (text, sanitized to prevent secret leakage)
  - timestamp (timestamp)
- **Relationships**: Belongs to Student Profile
- **Validation**: No PII in input/output fields, appropriate sanitization required
- **State transitions**: Created during each interaction → May be purged according to retention policy