#!/bin/bash

# AI Workspace - Full Stack Starter Script
# This script starts the entire application (backend + frontend)

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}"
echo "╔═══════════════════════════════════════════════════════════╗"
echo "║           🤖 AI Workspace - Starting Application          ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Get the directory where the script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$SCRIPT_DIR/backend"
FRONTEND_DIR="$SCRIPT_DIR/almo"

# Check if .env file exists in backend
if [ ! -f "$BACKEND_DIR/.env" ]; then
    echo -e "${RED}❌ Error: backend/.env file not found!${NC}"
    echo -e "${YELLOW}Please create it from the example:${NC}"
    echo "  cp backend/.env.example backend/.env"
    echo "  Then edit backend/.env with your actual credentials"
    exit 1
fi

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}❌ Error: Docker is not running!${NC}"
    echo "Please start Docker Desktop and try again."
    exit 1
fi

# Check if node_modules exists in frontend
if [ ! -d "$FRONTEND_DIR/node_modules" ]; then
    echo -e "${YELLOW}📦 Installing frontend dependencies...${NC}"
    cd "$FRONTEND_DIR"
    npm install
    cd "$SCRIPT_DIR"
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
echo -e "${BLUE}🐳 Starting backend services with Docker...${NC}"
cd "$BACKEND_DIR"

# Build and start Docker containers in background
docker-compose up --build -d

# Wait for services to be healthy
echo -e "${YELLOW}⏳ Waiting for services to be ready...${NC}"
sleep 5

# Check if web service is running
if docker-compose ps | grep -q "web.*Up"; then
    echo -e "${GREEN}✅ Backend services started successfully${NC}"
else
    echo -e "${RED}❌ Backend services failed to start${NC}"
    docker-compose logs --tail=50
    exit 1
fi

# Run migrations
echo -e "${BLUE}🔄 Running database migrations...${NC}"
docker-compose exec -T web python manage.py migrate --noinput
docker-compose exec -T web python manage.py setup_initial_data || true

echo -e "${GREEN}✅ Database ready${NC}"

# Start Frontend
echo -e "${BLUE}⚛️  Starting React frontend...${NC}"
cd "$FRONTEND_DIR"

# Start frontend in background
npm start &
FRONTEND_PID=$!

# Wait a moment for frontend to start
sleep 3

echo -e "${GREEN}"
echo "╔═══════════════════════════════════════════════════════════╗"
echo "║              🎉 Application Started Successfully!         ║"
echo "╠═══════════════════════════════════════════════════════════╣"
echo "║                                                           ║"
echo "║  Frontend:    http://localhost:3000                       ║"
echo "║  Backend API: http://localhost:8000                       ║"
echo "║  API Docs:    http://localhost:8000/swagger/              ║"
echo "║                                                           ║"
echo "╠═══════════════════════════════════════════════════════════╣"
echo "║  Press Ctrl+C to stop all services                        ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Show backend logs in background
echo -e "${YELLOW}📋 Showing backend logs (Ctrl+C to stop):${NC}"
cd "$BACKEND_DIR"
docker-compose logs -f web worker
