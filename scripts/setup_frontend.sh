#!/bin/bash

# Script to set up and run the Swym Social frontend

# Set up colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}Setting up Swym Social Frontend...${NC}"

# Navigate to frontend directory
cd app/frontend

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo -e "${RED}Node.js is not installed. Please install it before continuing.${NC}"
    exit 1
fi

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    echo -e "${RED}npm is not installed. Please install it before continuing.${NC}"
    exit 1
fi

# Install dependencies
echo -e "${GREEN}Installing dependencies...${NC}"
npm install

# Start the development server
echo -e "${GREEN}Starting the development server...${NC}"
echo -e "${BLUE}The frontend will be available at http://localhost:3000${NC}"
npm start 