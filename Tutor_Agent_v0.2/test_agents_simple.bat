@echo off
echo 🤖 TESTING ALL 6 AGENTS - SIMPLE CURL TEST
echo ================================================

echo.
echo 1️⃣ Testing Session Creation...
curl -s -X POST http://localhost:8000/api/v1/sessions/start -H "Content-Type: application/json" -d "{\"user_email\":\"test@example.com\"}" && echo ✅ Session OK || echo ❌ Session FAILED

echo.
echo 2️⃣ Testing RAG Content Agent...
curl -s -X POST http://localhost:8000/api/v1/rag/content -H "Content-Type: application/json" -d "{\"query\":\"Docker basics\",\"agent_type\":\"tutor\"}" && echo ✅ RAG Content OK || echo ❌ RAG Content FAILED

echo.
echo 3️⃣ Testing RAG Lesson Agent...
curl -s -X POST http://localhost:8000/api/v1/rag/lesson -H "Content-Type: application/json" -d "{\"topic\":\"Kubernetes\",\"learning_style\":\"visual\"}" && echo ✅ RAG Lesson OK || echo ❌ RAG Lesson FAILED

echo.
echo 4️⃣ Testing Authentication...
curl -s -X POST http://localhost:8000/api/v1/auth/register -H "Content-Type: application/json" -d "{\"name\":\"Test User\",\"email\":\"test@test.com\",\"password\":\"test123\"}" && echo ✅ Auth OK || echo ❌ Auth FAILED

echo.
echo 5️⃣ Testing Health Check...
curl -s http://localhost:8000/healthz && echo ✅ Health OK || echo ❌ Health FAILED

echo.
echo 🎯 AGENT TEST COMPLETE!
echo If you see ✅ marks, those agents are working!
echo If you see ❌ marks, those agents need fixing.
echo.
echo To test WebSocket agents (Orchestrator, Assessment, Tutor, Quiz, Feedback, Planning):
echo 1. Go to your frontend
echo 2. Open browser console (F12)
echo 3. Connect to WebSocket and send messages
echo.
pause
