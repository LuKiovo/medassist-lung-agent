@echo off
setlocal

cd /d "%~dp0"

echo [MedAssist] Starting MedAssist Lung Agent...
echo [MedAssist] This launcher does not train models or run heavy GPU jobs.

if not exist ".venv\Scripts\python.exe" (
    echo [MedAssist] Creating virtual environment...
    python -m venv .venv
    if errorlevel 1 goto error
)

call ".venv\Scripts\activate.bat"

echo [MedAssist] Installing or checking dependencies...
python -m pip install -r requirements.txt
if errorlevel 1 goto error

echo [MedAssist] Building RAG index...
python scripts\build_rag_index.py
if errorlevel 1 goto error

echo [MedAssist] Opening http://127.0.0.1:8000/
start "" "http://127.0.0.1:8000/"

echo [MedAssist] Press Ctrl+C in this window to stop the service.
python -m uvicorn medassist_lung_agent.main:app --host 127.0.0.1 --port 8000
goto end

:error
echo [MedAssist] Startup failed. Check the error message above.
pause

:end
endlocal
