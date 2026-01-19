@echo off
REM Start Docker Desktop and wait for it to be ready

echo ========================================
echo   Docker Desktop Startup Script
echo ========================================
echo.

echo [INFO] Checking if Docker Desktop is running...
docker version >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo [SUCCESS] Docker is already running!
    goto :build
)

echo [INFO] Docker is not running. Starting Docker Desktop...
echo.

REM Check if Docker Desktop is installed
if not exist "C:\Program Files\Docker\Docker\Docker Desktop.exe" (
    echo [ERROR] Docker Desktop not found at expected location.
    echo [ERROR] Please install Docker Desktop from: https://www.docker.com/products/docker-desktop/
    pause
    exit /b 1
)

REM Start Docker Desktop
echo [INFO] Launching Docker Desktop...
start "" "C:\Program Files\Docker\Docker\Docker Desktop.exe"
echo.

echo [INFO] Waiting for Docker to start (this may take 30-60 seconds)...
echo.

REM Wait for Docker to be ready
set "TIMEOUT=120"
set "ELAPSED=0"
set "INTERVAL=5"

:wait_loop
timeout /t %INTERVAL% /nobreak >nul 2>&1
set /a ELAPSED=%ELAPSED%+%INTERVAL%

docker version >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo [SUCCESS] Docker is now running!
    echo.
    goto :build
)

if %ELAPSED% GEQ %TIMEOUT% (
    echo [WARNING] Timeout waiting for Docker to start.
    echo [WARNING] Please check Docker Desktop manually.
    pause
    exit /b 1
)

echo [INFO] Still waiting... (%ELAPSED%/%TIMEOUT% seconds)
goto :wait_loop

:build
echo ========================================
echo   Docker is Ready - Building Images
echo ========================================
echo.

echo [INFO] Would you like to build the Docker images now? (Y/N)
set /p BUILD_NOW="> "

if /i "%BUILD_NOW%"=="Y" (
    echo.
    echo [INFO] Starting Docker build...
    call start.bat
) else (
    echo [INFO] Skipping build. Run "start.bat" when ready.
)

echo.
echo [INFO] Docker Desktop is ready to use!
pause
