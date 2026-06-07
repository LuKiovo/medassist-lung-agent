@echo off
setlocal

cd /d "%~dp0"

echo [MedAssist] Starting MedAssist Lung Agent...
echo [MedAssist] This launcher does not train models or run heavy GPU jobs.

set "PY_BOOTSTRAP="
where py >nul 2>nul
if not errorlevel 1 set "PY_BOOTSTRAP=py"

if "%PY_BOOTSTRAP%"=="" (
    where python >nul 2>nul
    if not errorlevel 1 set "PY_BOOTSTRAP=python"
)

if "%PY_BOOTSTRAP%"=="" (
    echo [MedAssist] Could not find Python launcher. Please install Python or make sure "py" is available.
    goto error
)

if not exist ".venv\Scripts\python.exe" (
    echo [MedAssist] Creating virtual environment with %PY_BOOTSTRAP%...
    %PY_BOOTSTRAP% -m venv .venv
    if errorlevel 1 goto error
)

call ".venv\Scripts\activate.bat"
set "PYTHON_EXE=%CD%\.venv\Scripts\python.exe"

echo [MedAssist] Installing or checking dependencies...
"%PYTHON_EXE%" -m pip install -r requirements.txt
if errorlevel 1 goto error

echo [MedAssist] Building RAG index...
"%PYTHON_EXE%" scripts\build_rag_index.py
if errorlevel 1 goto error

echo [MedAssist] Opening http://127.0.0.1:8000/
start "" "http://127.0.0.1:8000/"

echo [MedAssist] Press Ctrl+C in this window to stop the service.
"%PYTHON_EXE%" -m uvicorn medassist_lung_agent.main:app --host 127.0.0.1 --port 8000
goto end

:error
echo [MedAssist] Startup failed. Check the error message above.
pause

:end
endlocal
