#!/bin/bash

# AI Workspace - Full Stack Starter Script
# This script starts the entire application (backend + frontend)
# Usage: ./start.sh [--backend-only] [--frontend-only] [--stop]

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Get the directory where the script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$SCRIPT_DIR/backend"
FRONTEND_DIR="$SCRIPT_DIR/almo"

# Parse command line arguments
BACKEND_ONLY=false
FRONTEND_ONLY=false
STOP_ALL=false

for arg in "$@"; do
    case $arg in
        --backend-only)
            BACKEND_ONLY=true
            ;;
        --frontend-only)
            FRONTEND_ONLY=true
            ;;
        --stop)
            STOP_ALL=true
            ;;
        --help|-h)
            echo "Usage: ./start.sh [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --backend-only   Start only the backend services (Docker)"
            echo "  --frontend-only  Start only the frontend (requires backend running)"
            echo "  --stop           Stop all running services"
            echo "  --help, -h       Show this help message"
            echo ""
            echo "Default: Starts both backend and frontend"
            exit 0
            ;;
    esac
done

# Stop all services
if [ "$STOP_ALL" = true ]; then
    echo -e "${YELLOW}🛑 Stopping all services...${NC}"
    cd "$BACKEND_DIR"
    docker-compose down 2>/dev/null || true
    pkill -f "react-scripts start" 2>/dev/null || true
    echo -e "${GREEN}✅ All services stopped${NC}"
    exit 0
fi

echo -e "${BLUE}"
echo "╔═══════════════════════════════════════════════════════════╗"
echo "║           🤖 AI Workspace - Starting Application          ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Check if .env file exists in backend
if [ ! -f "$BACKEND_DIR/.env" ]; then
    echo -e "${RED}❌ Error: backend/.env file not found!${NC}"
    echo ""
    echo -e "${YELLOW}To fix this, run:${NC}"
    echo -e "  ${CYAN}cp backend/.env.example backend/.env${NC}"
    echo ""
    echo -e "${YELLOW}Then edit backend/.env with your credentials:${NC}"
    echo "  - AWS_ACCESS_KEY_ID"
    echo "  - AWS_SECRET_ACCESS_KEY"
    echo "  - AWS_STORAGE_BUCKET_NAME"
    echo "  - AWS_S3_REGION_NAME"
    echo "  - GROQ_API_KEY (get free at https://console.groq.com)"
    echo ""
    exit 1
fi

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}❌ Error: Docker is not running!${NC}"
    echo "Please start Docker Desktop and try again."
    exit 1
fi

# Function to cleanup on exit
cleanup() {
    echo -e "\n${YELLOW}🛑 Shutting down...${NC}"
    
    # Kill frontend process if running
    if [ ! -z "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null || true
    fi
    
    # Stop Docker containers
    echo -e "${YELLOW}Stopping Docker containers...${NC}"
    cd "$BACKEND_DIR"
    docker-compose down
    
    echo -e "${GREEN}✅ Application stopped successfully${NC}"
    exit 0
}

# Set up trap for cleanup
trap cleanup SIGINT SIGTERM

# Start Backend Services (Docker)
if [ "$FRONTEND_ONLY" = false ]; then
    echo -e "${BLUE}🐳 Starting backend services with Docker...${NC}"
    cd "$BACKEND_DIR"
    
    # Build and start Docker containers in background
    docker-compose up --build -d
    
    # Wait for services to be healthy
    echo -e "${YELLOW}⏳ Waiting for services to be ready...${NC}"
    sleep 8
    
    # Check if web service is running
    if docker-compose ps | grep -q "web.*Up\|web.*running"; then
        echo -e "${GREEN}✅ Backend services started successfully${NC}"
    else
        echo -e "${RED}❌ Backend services failed to start${NC}"
        echo -e "${YELLOW}Showing recent logs:${NC}"
        docker-compose logs --tail=50
        exit 1
    fi
    
    # Run migrations
    echo -e "${BLUE}🔄 Running database migrations...${NC}"
    docker-compose exec -T web python manage.py migrate --noinput 2>/dev/null || true
    docker-compose exec -T web python manage.py setup_initial_data 2>/dev/null || true
    
    echo -e "${GREEN}✅ Database ready${NC}"
fi

# Start Frontend
if [ "$BACKEND_ONLY" = false ]; then
    # Check if node_modules exists in frontend
    if [ ! -d "$FRONTEND_DIR/node_modules" ]; then
        echo -e "${YELLOW}📦 Installing frontend dependencies (first run)...${NC}"
        cd "$FRONTEND_DIR"
        npm install
        cd "$SCRIPT_DIR"
    fi
    
    echo -e "${BLUE}⚛️  Starting React frontend...${NC}"
    cd "$FRONTEND_DIR"
    
    # Start frontend in background
    npm start &
    FRONTEND_PID=$!
    
    # Wait a moment for frontend to start
    sleep 3
fi

echo -e "${GREEN}"
echo "╔═══════════════════════════════════════════════════════════╗"
echo "║              🎉 Application Started Successfully!         ║"
echo "╠═══════════════════════════════════════════════════════════╣"
echo "║                                                           ║"
echo "║  🌐 Frontend:     http://localhost:3000                   ║"
echo "║  🔌 Backend API:  http://localhost:8000                   ║"
echo "║  📚 API Docs:     http://localhost:8000/swagger/          ║"
echo "║                                                           ║"
echo "╠═══════════════════════════════════════════════════════════╣"
echo "║                                                           ║"
echo "║  📝 Quick Start:                                          ║"
echo "║     1. Open http://localhost:3000                         ║"
echo "║     2. Sign up for a new account                          ║"
echo "║     3. Upload a document (PDF, DOCX, or TXT)              ║"
echo "║     4. Chat with AI about your documents!                 ║"
echo "║                                                           ║"
echo "╠═══════════════════════════════════════════════════════════╣"
echo "║  Press Ctrl+C to stop all services                        ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# If backend only, show logs
if [ "$BACKEND_ONLY" = true ]; then
    echo -e "${YELLOW}📋 Showing backend logs (Ctrl+C to stop):${NC}"
    cd "$BACKEND_DIR"
    docker-compose logs -f web worker
else
    # Keep script running and show backend logs
    echo -e "${YELLOW}📋 Showing backend logs (Ctrl+C to stop):${NC}"
    cd "$BACKEND_DIR"
    docker-compose logs -f web worker
fi
