@echo off
echo 🚀 Starting Tutor GPT Backend Server...
echo.

cd backend
set PYTHONPATH=.
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

pause
