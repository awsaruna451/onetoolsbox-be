#!/bin/bash

# YouTube Caption Extractor API - Run Script

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}YouTube Caption Extractor API${NC}"
echo "================================"

# Check if virtual environment exists
if [ ! -d "youtubev" ]; then
    echo -e "${YELLOW}Virtual environment not found. Creating...${NC}"
    python3 -m venv youtubev
    echo -e "${GREEN}Virtual environment created.${NC}"
fi

# Activate virtual environment
echo -e "${YELLOW}Activating virtual environment...${NC}"
source youtubev/bin/activate

# Check if dependencies are installed
if [ ! -f "youtubev/bin/uvicorn" ]; then
    echo -e "${YELLOW}Installing dependencies...${NC}"
    pip install -r requirements.txt
    echo -e "${GREEN}Dependencies installed.${NC}"
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}Creating .env file from .env.example...${NC}"
    cp .env.example .env
    echo -e "${GREEN}.env file created. Please configure it as needed.${NC}"
fi

# Run the application
echo -e "${GREEN}Starting application...${NC}"
echo "================================"
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

