#!/bin/bash

# YouTube Caption Extractor API - Production Run Script

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}YouTube Caption Extractor API - Production Mode${NC}"
echo "================================================="

# Check if virtual environment exists
if [ ! -d "youtubev" ]; then
    echo -e "${RED}Error: Virtual environment not found.${NC}"
    echo "Please run: python3 -m venv youtubev && source youtubev/bin/activate && pip install -r requirements.txt"
    exit 1
fi

# Activate virtual environment
source youtubev/bin/activate

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo -e "${RED}Error: .env file not found.${NC}"
    echo "Please create .env file from .env.example"
    exit 1
fi

# Number of workers (default: 4)
WORKERS=${WORKERS:-4}

# Port (default: 8000)
PORT=${PORT:-8000}

# Run with Gunicorn
echo -e "${GREEN}Starting application with Gunicorn (${WORKERS} workers on port ${PORT})...${NC}"
echo "================================================="

gunicorn app.main:app \
    --workers $WORKERS \
    --worker-class uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:$PORT \
    --access-logfile - \
    --error-logfile - \
    --log-level info

