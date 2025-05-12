#!/bin/bash

# Script to start both the backend and frontend services for Swym Social

# Set up colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}Starting Swym Social Application...${NC}"

# Check if the virtual environment is activated
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo -e "${YELLOW}Python virtual environment not activated. Attempting to activate...${NC}"
    if [ -d "venv" ]; then
        source venv/bin/activate
        echo -e "${GREEN}Virtual environment activated.${NC}"
    else
        echo -e "${RED}Virtual environment directory 'venv' not found.${NC}"
        echo -e "${YELLOW}Creating a new virtual environment...${NC}"
        python3 -m venv venv
        source venv/bin/activate
        echo -e "${GREEN}Virtual environment created and activated.${NC}"
        
        # Install Python dependencies
        echo -e "${GREEN}Installing Python dependencies...${NC}"
        pip install -r requirements.txt
    fi
fi

# Start backend in background
echo -e "${GREEN}Starting backend server...${NC}"
python main.py &
BACKEND_PID=$!
echo -e "${BLUE}Backend server started with PID: $BACKEND_PID${NC}"
echo -e "${BLUE}The API will be available at http://localhost:8000${NC}"

# Wait a moment for the backend to start
echo -e "${YELLOW}Waiting for backend to initialize...${NC}"
sleep 3

# Start frontend
echo -e "${GREEN}Starting frontend development server...${NC}"
cd app/frontend

# Check if node_modules exists, if not, install dependencies
if [ ! -d "node_modules" ]; then
    echo -e "${YELLOW}Node modules not found. Installing dependencies...${NC}"
    npm install
fi

echo -e "${BLUE}Frontend will be available at http://localhost:3000${NC}"
npm start

# When Ctrl+C is pressed, kill the backend process
trap "echo -e '${YELLOW}Shutting down services...${NC}'; kill $BACKEND_PID; exit" INT TERM 