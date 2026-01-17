@echo off
REM Sphota Server Startup Script (Windows Batch)
REM Starts the Streamlit development server for Sphota.AI

setlocal enabledelayedexpansion

echo.
echo =====================================================================
echo   Sphota: Cognitive Meaning Engine Server
echo =====================================================================
echo.

cd /d "%~dp0"

REM Check if venv exists
if not exist ".venv" (
    echo Creating virtual environment...
    python -m venv .venv
)

REM Activate virtual environment
call .venv\Scripts\activate.bat

REM Install requirements
echo Installing dependencies...
pip install -r requirements.txt --quiet

REM Start server
echo.
echo Starting Streamlit server...
echo Access the app at: http://localhost:8501
echo.
echo Press Ctrl+C to stop the server
echo.

python -m streamlit run app.py --server.port 8501

pause
