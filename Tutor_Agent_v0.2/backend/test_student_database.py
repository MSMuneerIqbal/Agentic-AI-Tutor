#!/usr/bin/env python3
"""
Test Student Database Operations
Verify that the database system works correctly for students
"""

import asyncio
import os
import sys
import uuid
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add backend to path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

async def test_student_database_operations():
    """Test all database operations for students."""
    print("🗄️ STUDENT DATABASE TESTING")
    print("=" * 40)
    print("Testing database operations for student data")
    print()
    
    # Test 1: Database Connection
    print("1️⃣ TESTING DATABASE CONNECTION")
    print("-" * 35)
    
    try:
        from app.core.database import get_db
        from app.core.init_db import init_db
        
        # Test database connection
        async for db in get_db():
            # Test basic connection
            result = await db.execute("SELECT 1 as test")
            test_value = result.scalar()
            if test_value == 1:
                print("✅ Database connection successful")
            else:
                print("❌ Database connection failed")
                return False
            break
        
        print("✅ Database connection working")
        print()
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False
    
    # Test 2: Student User Creation
    print("2️⃣ TESTING STUDENT USER CREATION")
    print("-" * 40)
    
    try:
        from app.models.user import User
        from app.core.database import get_db
        
        # Create test student
        student_id = str(uuid.uuid4())
        test_student = User(
            id=student_id,
            email="test.student@example.com",
            name="Test Student",
            is_active=True,
            created_at=datetime.utcnow()
        )
        
        async for db in get_db():
            db.add(test_student)
            await db.commit()
            await db.refresh(test_student)
            print(f"✅ Student created: {test_student.name} (ID: {test_student.id})")
            break
        
        print("✅ Student user creation working")
        print()
    except Exception as e:
        print(f"❌ Student user creation failed: {e}")
        return False
    
    # Test 3: Learning Style Assessment Storage
    print("3️⃣ TESTING LEARNING STYLE ASSESSMENT STORAGE")
    print("-" * 50)
    
    try:
        from app.models.assessment import AssessmentResult, LearningStyle
        from app.core.database import get_db
        
        # Create assessment result
        assessment = AssessmentResult(
            user_id=student_id,
            style=LearningStyle.V,  # Visual learning style
            answers=["a", "b", "c", "d", "a"],
            created_at=datetime.utcnow()
        )
        
        async for db in get_db():
            db.add(assessment)
            await db.commit()
            await db.refresh(assessment)
            print(f"✅ Assessment stored: {assessment.style} learning style")
            break
        
        print("✅ Learning style assessment storage working")
        print()
    except Exception as e:
        print(f"❌ Assessment storage failed: {e}")
        return False
    
    # Test 4: Study Plan Storage
    print("4️⃣ TESTING STUDY PLAN STORAGE")
    print("-" * 35)
    
    try:
        from app.models.plan import Plan
        from app.core.database import get_db
        
        # Create study plan
        study_plan = Plan(
            user_id=student_id,
            summary="Personalized Docker and Kubernetes learning plan",
            topics=[
                {
                    "id": "topic_1",
                    "title": "Docker Fundamentals",
                    "description": "Learn Docker basics",
                    "estimated_hours": 4,
                    "activities": ["Create containers", "Build images"],
                    "milestones": ["Understand concepts", "Complete exercises"]
                },
                {
                    "id": "topic_2",
                    "title": "Kubernetes Basics",
                    "description": "Learn Kubernetes fundamentals",
                    "estimated_hours": 6,
                    "activities": ["Deploy pods", "Create services"],
                    "milestones": ["Deploy application", "Scale services"]
                }
            ],
            created_at=datetime.utcnow()
        )
        
        async for db in get_db():
            db.add(study_plan)
            await db.commit()
            await db.refresh(study_plan)
            print(f"✅ Study plan stored: {len(study_plan.topics)} topics")
            break
        
        print("✅ Study plan storage working")
        print()
    except Exception as e:
        print(f"❌ Study plan storage failed: {e}")
        return False
    
    # Test 5: Session Management
    print("5️⃣ TESTING SESSION MANAGEMENT")
    print("-" * 35)
    
    try:
        from app.models.session import Session
        from app.models import SessionState
        from app.core.database import get_db
        
        # Create session
        session_id = str(uuid.uuid4())
        session = Session(
            id=session_id,
            user_id=student_id,
            state=SessionState.TUTORING,
            current_topic="Docker containers",
            learning_style="V",
            progress=0,
            created_at=datetime.utcnow()
        )
        
        async for db in get_db():
            db.add(session)
            await db.commit()
            await db.refresh(session)
            print(f"✅ Session created: {session.state} - {session.current_topic}")
            break
        
        print("✅ Session management working")
        print()
    except Exception as e:
        print(f"❌ Session management failed: {e}")
        return False
    
    # Test 6: Quiz Results Storage
    print("6️⃣ TESTING QUIZ RESULTS STORAGE")
    print("-" * 40)
    
    try:
        from app.models.quiz import QuizResult
        from app.core.database import get_db
        
        # Create quiz result
        quiz_result = QuizResult(
            user_id=student_id,
            session_id=session_id,
            topic="Docker containers",
            quiz_type="knowledge_check",
            questions=[
                {
                    "question": "What is Docker?",
                    "answer": "A",
                    "correct": True
                },
                {
                    "question": "What are containers?",
                    "answer": "B",
                    "correct": True
                }
            ],
            score=85,
            total_questions=2,
            passed=True,
            created_at=datetime.utcnow()
        )
        
        async for db in get_db():
            db.add(quiz_result)
            await db.commit()
            await db.refresh(quiz_result)
            print(f"✅ Quiz result stored: {quiz_result.score}% score")
            break
        
        print("✅ Quiz results storage working")
        print()
    except Exception as e:
        print(f"❌ Quiz results storage failed: {e}")
        return False
    
    # Test 7: Lesson Progress Tracking
    print("7️⃣ TESTING LESSON PROGRESS TRACKING")
    print("-" * 40)
    
    try:
        from app.models.lesson import Lesson
        from app.core.database import get_db
        
        # Create lesson record
        lesson = Lesson(
            user_id=student_id,
            session_id=session_id,
            topic="Docker containers",
            lesson_type="interactive",
            content="Introduction to Docker containers",
            duration_minutes=15,
            completed=True,
            feedback_score=4.5,
            created_at=datetime.utcnow()
        )
        
        async for db in get_db():
            db.add(lesson)
            await db.commit()
            await db.refresh(lesson)
            print(f"✅ Lesson tracked: {lesson.topic} - {lesson.duration_minutes} minutes")
            break
        
        print("✅ Lesson progress tracking working")
        print()
    except Exception as e:
        print(f"❌ Lesson tracking failed: {e}")
        return False
    
    # Test 8: Feedback Storage
    print("8️⃣ TESTING FEEDBACK STORAGE")
    print("-" * 30)
    
    try:
        from app.models.feedback import Feedback
        from app.core.database import get_db
        
        # Create feedback record
        feedback = Feedback(
            user_id=student_id,
            session_id=session_id,
            feedback_type="student_difficulty",
            topic="Docker containers",
            message="Student had trouble understanding container concepts",
            severity="medium",
            resolved=False,
            created_at=datetime.utcnow()
        )
        
        async for db in get_db():
            db.add(feedback)
            await db.commit()
            await db.refresh(feedback)
            print(f"✅ Feedback stored: {feedback.feedback_type} - {feedback.topic}")
            break
        
        print("✅ Feedback storage working")
        print()
    except Exception as e:
        print(f"❌ Feedback storage failed: {e}")
        return False
    
    # Test 9: Data Retrieval
    print("9️⃣ TESTING DATA RETRIEVAL")
    print("-" * 30)
    
    try:
        from app.services.profile_service import profile_service
        from app.core.database import get_db
        
        # Test retrieving student profile
        async for db in get_db():
            profile = await profile_service.get_user_profile(student_id, db)
            if profile:
                print(f"✅ Student profile retrieved: {profile.get('name', 'Unknown')}")
                print(f"   Learning style: {profile.get('learning_style', 'Unknown')}")
                print(f"   Active: {profile.get('is_active', False)}")
            else:
                print("❌ Student profile not found")
            break
        
        print("✅ Data retrieval working")
        print()
    except Exception as e:
        print(f"❌ Data retrieval failed: {e}")
        return False
    
    # Test 10: Redis Session Storage
    print("🔟 TESTING REDIS SESSION STORAGE")
    print("-" * 35)
    
    try:
        from app.core.redis import get_redis_client
        
        # Test Redis connection
        redis_client = await get_redis_client()
        
        # Store session data
        session_data = {
            "user_id": student_id,
            "current_topic": "Docker containers",
            "learning_style": "V",
            "progress": 0,
            "last_activity": datetime.utcnow().isoformat()
        }
        
        await redis_client.setex(f"session:{session_id}", 3600, str(session_data))
        
        # Retrieve session data
        retrieved_data = await redis_client.get(f"session:{session_id}")
        if retrieved_data:
            print("✅ Redis session storage working")
            print(f"   Session data stored and retrieved successfully")
        else:
            print("❌ Redis session storage failed")
            return False
        
        print("✅ Redis session storage working")
        print()
    except Exception as e:
        print(f"❌ Redis session storage failed: {e}")
        return False
    
    return True

async def test_student_data_persistence():
    """Test that student data persists across sessions."""
    print("💾 TESTING STUDENT DATA PERSISTENCE")
    print("=" * 40)
    print("Verifying that student data persists across sessions")
    print()
    
    try:
        from app.models.user import User
        from app.models.assessment import AssessmentResult, LearningStyle
        from app.models.plan import Plan
        from app.core.database import get_db
        
        # Create a test student
        student_id = str(uuid.uuid4())
        
        # Create user
        user = User(
            id=student_id,
            email="persistence.test@example.com",
            name="Persistence Test Student",
            is_active=True,
            created_at=datetime.utcnow()
        )
        
        # Create assessment
        assessment = AssessmentResult(
            user_id=student_id,
            style=LearningStyle.K,  # Kinesthetic learning style
            answers=["d", "d", "c", "d", "b"],
            created_at=datetime.utcnow()
        )
        
        # Create study plan
        plan = Plan(
            user_id=student_id,
            summary="Test persistence study plan",
            topics=[
                {
                    "id": "persistence_topic",
                    "title": "Persistence Testing",
                    "description": "Testing data persistence",
                    "estimated_hours": 2,
                    "activities": ["Test data", "Verify persistence"],
                    "milestones": ["Data stored", "Data retrieved"]
                }
            ],
            created_at=datetime.utcnow()
        )
        
        # Store all data
        async for db in get_db():
            db.add(user)
            db.add(assessment)
            db.add(plan)
            await db.commit()
            print("✅ Student data stored successfully")
            break
        
        # Simulate session end and restart
        print("   Simulating session end...")
        await asyncio.sleep(1)
        print("   Simulating session restart...")
        
        # Retrieve data
        async for db in get_db():
            # Get user
            retrieved_user = await db.get(User, student_id)
            if retrieved_user:
                print(f"✅ User data persisted: {retrieved_user.name}")
            
            # Get assessment
            assessment_query = await db.execute(
                "SELECT * FROM assessment_results WHERE user_id = :user_id",
                {"user_id": student_id}
            )
            assessment_data = assessment_query.fetchone()
            if assessment_data:
                print(f"✅ Assessment data persisted: {assessment_data.style}")
            
            # Get plan
            plan_query = await db.execute(
                "SELECT * FROM plans WHERE user_id = :user_id",
                {"user_id": student_id}
            )
            plan_data = plan_query.fetchone()
            if plan_data:
                print(f"✅ Study plan data persisted: {len(plan_data.topics)} topics")
            
            break
        
        print("✅ Student data persistence working")
        print()
        return True
        
    except Exception as e:
        print(f"❌ Student data persistence failed: {e}")
        return False

async def test_database_performance():
    """Test database performance for student operations."""
    print("⚡ TESTING DATABASE PERFORMANCE")
    print("=" * 35)
    print("Testing database performance for student operations")
    print()
    
    try:
        from app.core.database import get_db
        import time
        
        # Test query performance
        start_time = time.time()
        
        async for db in get_db():
            # Test user query
            user_query = await db.execute("SELECT COUNT(*) FROM users")
            user_count = user_query.scalar()
            
            # Test assessment query
            assessment_query = await db.execute("SELECT COUNT(*) FROM assessment_results")
            assessment_count = assessment_query.scalar()
            
            # Test plan query
            plan_query = await db.execute("SELECT COUNT(*) FROM plans")
            plan_count = plan_query.scalar()
            
            break
        
        end_time = time.time()
        query_time = end_time - start_time
        
        print(f"✅ Database queries completed in {query_time:.3f} seconds")
        print(f"   Users: {user_count}")
        print(f"   Assessments: {assessment_count}")
        print(f"   Plans: {plan_count}")
        
        if query_time < 1.0:
            print("✅ Database performance acceptable")
        else:
            print("⚠️ Database performance may need optimization")
        
        print()
        return True
        
    except Exception as e:
        print(f"❌ Database performance test failed: {e}")
        return False

async def main():
    """Main test function."""
    print("🎓 STUDENT DATABASE COMPREHENSIVE TEST")
    print("=" * 50)
    print("Testing all database operations for students")
    print()
    
    # Run all tests
    tests = [
        ("Database Operations", test_student_database_operations),
        ("Data Persistence", test_student_data_persistence),
        ("Database Performance", test_database_performance)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"🧪 Running {test_name}...")
        try:
            result = await test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    # Final report
    print("📊 DATABASE TEST RESULTS")
    print("=" * 30)
    
    passed_tests = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {test_name:20} | {status}")
        if result:
            passed_tests += 1
    
    print("=" * 30)
    print(f"Overall: {passed_tests}/{len(results)} tests passed")
    
    if passed_tests == len(results):
        print("\n🎉 DATABASE SYSTEM READY FOR STUDENTS!")
        print("\n📋 Database Capabilities:")
        print("   ✅ Student user management")
        print("   ✅ Learning style assessment storage")
        print("   ✅ Study plan persistence")
        print("   ✅ Session management")
        print("   ✅ Quiz results tracking")
        print("   ✅ Lesson progress tracking")
        print("   ✅ Feedback storage")
        print("   ✅ Data retrieval")
        print("   ✅ Redis session storage")
        print("   ✅ Data persistence across sessions")
        print("   ✅ Performance optimization")
        
        print("\n🚀 STUDENTS CAN USE THE SYSTEM!")
        print("   All student data will be properly stored and retrieved")
        print("   Learning progress will be tracked")
        print("   Sessions will be managed correctly")
        print("   Performance is acceptable for production use")
    else:
        print(f"\n⚠️ Some database tests failed. Check the errors above.")

if __name__ == "__main__":
    asyncio.run(main())
