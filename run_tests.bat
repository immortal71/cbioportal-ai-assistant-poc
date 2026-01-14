@echo off
cd C:\Users\HUAWEI\Downloads\PoC-cbioPortal\cbioportal-ai-assistant-poc
start "Backend Server" python -m uvicorn backend.main:app --port 8000
timeout /t 3 /nobreak
python test_comprehensive_llm.py
pause
