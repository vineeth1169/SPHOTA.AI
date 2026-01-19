#!/bin/bash

###############################################################################
# Sphota Hybrid Engine - Containerized Startup Script
#
# This script orchestrates the startup of the Hybrid Sphota Engine in Docker:
# 1. Builds Docker images (if needed)
# 2. Starts all services (MySQL, HuggingFace cache setup)
# 3. Waits for database to be healthy
# 4. Runs database migrations (creates tables)
# 5. Starts the FastAPI server
#
# Usage:
#   ./start.sh              # Normal startup
#   ./start.sh --rebuild    # Force rebuild of images
#   ./start.sh --logs       # Show logs after startup
###############################################################################

set -e  # Exit on any error

# Color codes for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'  # No Color

# Configuration
COMPOSE_FILE="docker-compose.yml"
ENV_FILE=".env.docker"
MIGRATION_SCRIPT="scripts/migrations.sql"
WAIT_TIMEOUT=120  # seconds

# Helper functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Parse command line arguments
REBUILD=false
SHOW_LOGS=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --rebuild)
            REBUILD=true
            shift
            ;;
        --logs)
            SHOW_LOGS=true
            shift
            ;;
        *)
            log_warning "Unknown argument: $1"
            shift
            ;;
    esac
done

###############################################################################
# Step 1: Check prerequisites
###############################################################################
log_info "Checking prerequisites..."

if ! command -v docker &> /dev/null; then
    log_error "Docker is not installed or not in PATH"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    log_error "Docker Compose is not installed or not in PATH"
    exit 1
fi

if [ ! -f "$COMPOSE_FILE" ]; then
    log_error "docker-compose.yml not found"
    exit 1
fi

log_success "Prerequisites check passed"

###############################################################################
# Step 2: Setup environment file if needed
###############################################################################
log_info "Setting up environment..."

if [ ! -f "$ENV_FILE" ]; then
    log_info "Creating .env.docker with default values..."
    cat > "$ENV_FILE" << 'EOF'
# Database Configuration
DB_HOST=sphota_db
DB_PORT=3306
DB_USER=sphota_user
DB_PASSWORD=sphota_secure_password
DB_NAME=sphota_db

# MySQL Root Password
MYSQL_ROOT_PASSWORD=root_secure_password

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
LOG_LEVEL=info

# Model Configuration
SBERT_MODEL=all-MiniLM-L6-v2

# ChromaDB Configuration
CHROMA_DATA_PATH=/app/chroma_data
EOF
    log_success "Environment file created"
else
    log_info "Using existing .env.docker"
fi

# Load environment variables
export $(cat "$ENV_FILE" | grep -v '#' | xargs)

###############################################################################
# Step 3: Build or pull Docker images
###############################################################################
log_info "Preparing Docker images..."

if [ "$REBUILD" = true ]; then
    log_warning "Rebuilding Docker images (--rebuild flag set)"
    docker-compose -f "$COMPOSE_FILE" build --no-cache
else
    log_info "Building/pulling Docker images..."
    docker-compose -f "$COMPOSE_FILE" build
fi

log_success "Docker images ready"

###############################################################################
# Step 4: Stop and remove existing containers (clean start)
###############################################################################
log_info "Removing any existing containers..."
docker-compose -f "$COMPOSE_FILE" down --volumes || true
log_info "Clean slate prepared"

###############################################################################
# Step 5: Start services
###############################################################################
log_info "Starting services..."
docker-compose -f "$COMPOSE_FILE" up -d

log_success "Services started"

###############################################################################
# Step 6: Wait for database to be healthy
###############################################################################
log_info "Waiting for database to be healthy (timeout: ${WAIT_TIMEOUT}s)..."

DB_CONTAINER="sphota_db"
ELAPSED=0
INTERVAL=5

while [ $ELAPSED -lt $WAIT_TIMEOUT ]; do
    if docker exec "$DB_CONTAINER" mysqladmin ping -h localhost -u "$DB_USER" -p"$DB_PASSWORD" &> /dev/null; then
        log_success "Database is healthy"
        break
    fi
    
    echo -n "."
    sleep $INTERVAL
    ELAPSED=$((ELAPSED + INTERVAL))
done

if [ $ELAPSED -ge $WAIT_TIMEOUT ]; then
    log_error "Database failed to become healthy within ${WAIT_TIMEOUT}s"
    log_error "Check logs with: docker-compose logs sphota_db"
    exit 1
fi

###############################################################################
# Step 7: Run database migrations
###############################################################################
log_info "Running database migrations..."

API_CONTAINER="sphota_api"

# Run Python migration script inside container
docker exec "$API_CONTAINER" python << 'PYTHON_EOF'
import os
import sys
import mysql.connector
from mysql.connector import Error

try:
    # Get database configuration from environment
    config = {
        'host': os.getenv('DB_HOST', 'localhost'),
        'port': int(os.getenv('DB_PORT', 3306)),
        'user': os.getenv('DB_USER', 'root'),
        'password': os.getenv('DB_PASSWORD', ''),
        'database': os.getenv('DB_NAME', 'sphota_db')
    }
    
    # Connect to database
    connection = mysql.connector.connect(**config)
    cursor = connection.cursor()
    
    print("[INFO] Connected to database successfully")
    
    # Create tables for Hybrid Sphota Engine
    
    # 1. Intents table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS intents (
        id VARCHAR(100) PRIMARY KEY,
        pure_text VARCHAR(255) NOT NULL,
        description TEXT,
        examples JSON,
        required_context JSON,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """)
    print("[SUCCESS] Created 'intents' table")
    
    # 2. Resolved Intents table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS resolved_intents (
        id INT AUTO_INCREMENT PRIMARY KEY,
        user_input VARCHAR(500) NOT NULL,
        intent_id VARCHAR(100) NOT NULL,
        raw_similarity FLOAT,
        context_adjusted_score FLOAT,
        confidence FLOAT,
        active_factors JSON,
        stage_1_passed BOOLEAN DEFAULT TRUE,
        stage_2_passed BOOLEAN DEFAULT TRUE,
        fallback_used BOOLEAN DEFAULT FALSE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (intent_id) REFERENCES intents(id),
        INDEX idx_intent (intent_id),
        INDEX idx_created (created_at)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """)
    print("[SUCCESS] Created 'resolved_intents' table")
    
    # 3. Feedback table (for Real-Time Learning)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS feedback (
        id INT AUTO_INCREMENT PRIMARY KEY,
        resolved_intent_id INT NOT NULL,
        user_input VARCHAR(500),
        intent_id VARCHAR(100),
        was_correct BOOLEAN,
        actual_intent_id VARCHAR(100),
        confidence_before FLOAT,
        confidence_after FLOAT,
        feedback_text TEXT,
        rating INT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (resolved_intent_id) REFERENCES resolved_intents(id),
        FOREIGN KEY (intent_id) REFERENCES intents(id),
        FOREIGN KEY (actual_intent_id) REFERENCES intents(id),
        INDEX idx_created (created_at)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """)
    print("[SUCCESS] Created 'feedback' table")
    
    # 4. Context History table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS context_history (
        id INT AUTO_INCREMENT PRIMARY KEY,
        resolved_intent_id INT NOT NULL,
        context_factors JSON,
        location VARCHAR(100),
        time VARCHAR(50),
        user_profile VARCHAR(100),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (resolved_intent_id) REFERENCES resolved_intents(id),
        INDEX idx_created (created_at)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """)
    print("[SUCCESS] Created 'context_history' table")
    
    connection.commit()
    cursor.close()
    connection.close()
    
    print("[SUCCESS] All database migrations completed successfully")
    
except Error as e:
    print(f"[ERROR] Database error: {e}")
    sys.exit(1)
except Exception as e:
    print(f"[ERROR] Unexpected error: {e}")
    sys.exit(1)
PYTHON_EOF

if [ $? -eq 0 ]; then
    log_success "Database migrations completed"
else
    log_error "Database migrations failed"
    exit 1
fi

###############################################################################
# Step 8: Verify API is running
###############################################################################
log_info "Verifying API is responsive..."

API_ENDPOINT="http://localhost:8000"
HEALTH_CHECK_TIMEOUT=60
ELAPSED=0

while [ $ELAPSED -lt $HEALTH_CHECK_TIMEOUT ]; do
    if curl -s "$API_ENDPOINT/health" &> /dev/null; then
        log_success "API is healthy and responsive"
        break
    fi
    
    echo -n "."
    sleep 2
    ELAPSED=$((ELAPSED + 2))
done

if [ $ELAPSED -ge $HEALTH_CHECK_TIMEOUT ]; then
    log_warning "API health check timed out (it may still be starting)"
fi

###############################################################################
# Step 9: Display startup summary
###############################################################################
log_success "Sphota Hybrid Engine is running!"
echo ""
echo -e "${GREEN}════════════════════════════════════════════════${NC}"
echo -e "${GREEN}   SPHOTA HYBRID ENGINE - STARTUP COMPLETE${NC}"
echo -e "${GREEN}════════════════════════════════════════════════${NC}"
echo ""
echo -e "${BLUE}API Endpoint:${NC}     http://localhost:8000"
echo -e "${BLUE}API Docs:${NC}         http://localhost:8000/docs"
echo -e "${BLUE}ReDoc:${NC}            http://localhost:8000/redoc"
echo -e "${BLUE}Database Host:${NC}    localhost:3306"
echo -e "${BLUE}Database Name:${NC}    $DB_NAME"
echo -e "${BLUE}ChromaDB Data:${NC}    ./chroma_data (persistent)"
echo ""
echo -e "${YELLOW}Useful Commands:${NC}"
echo "  View logs:       docker-compose logs -f sphota_api"
echo "  Stop services:   docker-compose down"
echo "  Restart services: docker-compose restart"
echo "  Clean restart:   ./start.sh --rebuild"
echo ""

###############################################################################
# Step 10: Optional - Show logs
###############################################################################
if [ "$SHOW_LOGS" = true ]; then
    log_info "Showing logs (press Ctrl+C to stop)..."
    docker-compose -f "$COMPOSE_FILE" logs -f sphota_api
fi

exit 0
