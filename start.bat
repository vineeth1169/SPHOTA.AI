@echo off
REM ============================================================================
REM Sphota Hybrid Engine - Windows Containerized Startup Script
REM
REM This batch file orchestrates the startup of the Hybrid Sphota Engine in Docker:
REM 1. Checks Docker installation
REM 2. Builds Docker images (if needed)
REM 3. Starts all services (MySQL, Cache, API)
REM 4. Waits for database to be healthy
REM 5. Runs database migrations (creates tables)
REM 6. Displays startup information
REM
REM Usage:
REM   start.bat              (Normal startup)
REM   start.bat rebuild      (Force rebuild of images)
REM   start.bat logs         (Show logs after startup)
REM ============================================================================

setlocal enabledelayedexpansion

REM Configuration
set COMPOSE_FILE=docker-compose.yml
set ENV_FILE=.env.docker
set WAIT_TIMEOUT=120
set API_CONTAINER=sphota_api
set DB_CONTAINER=sphota_db

REM Parse arguments
set REBUILD=false
set SHOW_LOGS=false

if "%1"=="rebuild" set REBUILD=true
if "%1"=="logs" set SHOW_LOGS=true

REM ============================================================================
REM Step 1: Check prerequisites
REM ============================================================================
echo [INFO] Checking prerequisites...

where docker >nul 2>nul
if errorlevel 1 (
    echo [ERROR] Docker is not installed or not in PATH
    exit /b 1
)

where docker-compose >nul 2>nul
if errorlevel 1 (
    echo [ERROR] Docker Compose is not installed or not in PATH
    exit /b 1
)

if not exist %COMPOSE_FILE% (
    echo [ERROR] docker-compose.yml not found
    exit /b 1
)

echo [SUCCESS] Prerequisites check passed

REM ============================================================================
REM Step 2: Setup environment file if needed
REM ============================================================================
echo [INFO] Setting up environment...

if not exist %ENV_FILE% (
    echo [INFO] Creating %ENV_FILE% with default values...
    (
        echo # Database Configuration
        echo DB_HOST=sphota_db
        echo DB_PORT=3306
        echo DB_USER=sphota_user
        echo DB_PASSWORD=sphota_secure_password
        echo DB_NAME=sphota_db
        echo.
        echo # MySQL Root Password
        echo MYSQL_ROOT_PASSWORD=root_secure_password
        echo.
        echo # API Configuration
        echo API_HOST=0.0.0.0
        echo API_PORT=8000
        echo LOG_LEVEL=info
        echo.
        echo # Model Configuration
        echo SBERT_MODEL=all-MiniLM-L6-v2
        echo.
        echo # ChromaDB Configuration
        echo CHROMA_DATA_PATH=/app/chroma_data
    ) > %ENV_FILE%
    echo [SUCCESS] Environment file created
) else (
    echo [INFO] Using existing %ENV_FILE%
)

REM ============================================================================
REM Step 3: Build or pull Docker images
REM ============================================================================
echo [INFO] Preparing Docker images...

if "%REBUILD%"=="true" (
    echo [WARNING] Rebuilding Docker images...
    docker-compose -f %COMPOSE_FILE% build --no-cache
) else (
    echo [INFO] Building/pulling Docker images...
    docker-compose -f %COMPOSE_FILE% build
)

if errorlevel 1 (
    echo [ERROR] Docker image build failed
    exit /b 1
)

echo [SUCCESS] Docker images ready

REM ============================================================================
REM Step 4: Stop and remove existing containers
REM ============================================================================
echo [INFO] Removing any existing containers...
docker-compose -f %COMPOSE_FILE% down --volumes
echo [INFO] Clean slate prepared

REM ============================================================================
REM Step 5: Start services
REM ============================================================================
echo [INFO] Starting services...
docker-compose -f %COMPOSE_FILE% up -d

if errorlevel 1 (
    echo [ERROR] Failed to start services
    exit /b 1
)

echo [SUCCESS] Services started

REM ============================================================================
REM Step 6: Wait for database to be healthy
REM ============================================================================
echo [INFO] Waiting for database to be healthy (timeout: %WAIT_TIMEOUT%s)...

setlocal enabledelayedexpansion
set ELAPSED=0
set INTERVAL=5

:wait_db_loop
if !ELAPSED! geq %WAIT_TIMEOUT% (
    echo [ERROR] Database failed to become healthy within %WAIT_TIMEOUT%s
    echo [ERROR] Check logs with: docker-compose logs sphota_db
    exit /b 1
)

docker exec %DB_CONTAINER% mysqladmin ping -h localhost -u sphota_user -psphota_secure_password >nul 2>nul
if errorlevel 0 (
    echo.
    echo [SUCCESS] Database is healthy
    goto :end_wait_db
)

echo|set /p="."
timeout /t %INTERVAL% /nobreak >nul
set /a ELAPSED=!ELAPSED! + %INTERVAL%
goto :wait_db_loop

:end_wait_db

REM ============================================================================
REM Step 7: Run database migrations
REM ============================================================================
echo [INFO] Running database migrations...

docker exec %API_CONTAINER% python -c ^
"^
import os; ^
import sys; ^
import mysql.connector; ^
^
try: ^
    config = { ^
        'host': os.getenv('DB_HOST', 'localhost'), ^
        'port': int(os.getenv('DB_PORT', 3306)), ^
        'user': os.getenv('DB_USER', 'root'), ^
        'password': os.getenv('DB_PASSWORD', ''), ^
        'database': os.getenv('DB_NAME', 'sphota_db') ^
    }; ^
    connection = mysql.connector.connect(**config); ^
    cursor = connection.cursor(); ^
    print('[INFO] Connected to database successfully'); ^
    ^
    cursor.execute('''CREATE TABLE IF NOT EXISTS intents ( ^
        id VARCHAR(100) PRIMARY KEY, ^
        pure_text VARCHAR(255) NOT NULL, ^
        description TEXT, ^
        examples JSON, ^
        required_context JSON, ^
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, ^
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP ^
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci'''); ^
    print('[SUCCESS] Created intents table'); ^
    ^
    cursor.execute('''CREATE TABLE IF NOT EXISTS resolved_intents ( ^
        id INT AUTO_INCREMENT PRIMARY KEY, ^
        user_input VARCHAR(500) NOT NULL, ^
        intent_id VARCHAR(100) NOT NULL, ^
        raw_similarity FLOAT, ^
        context_adjusted_score FLOAT, ^
        confidence FLOAT, ^
        active_factors JSON, ^
        stage_1_passed BOOLEAN DEFAULT TRUE, ^
        stage_2_passed BOOLEAN DEFAULT TRUE, ^
        fallback_used BOOLEAN DEFAULT FALSE, ^
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, ^
        FOREIGN KEY (intent_id) REFERENCES intents(id), ^
        INDEX idx_intent (intent_id), ^
        INDEX idx_created (created_at) ^
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci'''); ^
    print('[SUCCESS] Created resolved_intents table'); ^
    ^
    connection.commit(); ^
    cursor.close(); ^
    connection.close(); ^
    print('[SUCCESS] All database migrations completed successfully'); ^
except Exception as e: ^
    print(f'[ERROR] Database error: {e}'); ^
    sys.exit(1) ^
"

if errorlevel 1 (
    echo [ERROR] Database migrations failed
    exit /b 1
)

echo [SUCCESS] Database migrations completed

REM ============================================================================
REM Step 8: Display startup summary
REM ============================================================================
echo.
echo ════════════════════════════════════════════════
echo    SPHOTA HYBRID ENGINE - STARTUP COMPLETE
echo ════════════════════════════════════════════════
echo.
echo API Endpoint:      http://localhost:8000
echo API Docs:          http://localhost:8000/docs
echo ReDoc:             http://localhost:8000/redoc
echo Database Host:     localhost:3306
echo Database Name:     sphota_db
echo ChromaDB Data:     ./chroma_data (persistent)
echo.
echo Useful Commands:
echo   View logs:       docker-compose logs -f sphota_api
echo   Stop services:   docker-compose down
echo   Restart services: docker-compose restart
echo   Clean rebuild:   start.bat rebuild
echo.

REM ============================================================================
REM Step 9: Optional - Show logs
REM ============================================================================
if "%SHOW_LOGS%"=="true" (
    echo [INFO] Showing logs (press Ctrl+C to stop)...
    docker-compose -f %COMPOSE_FILE% logs -f sphota_api
)

endlocal
exit /b 0
