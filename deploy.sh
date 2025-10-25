#!/bin/bash

# YouTube Caption Extractor API - AWS Lambda Deployment Script

set -e

echo "🚀 Deploying YouTube Caption Extractor API to AWS Lambda"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if serverless is installed
if ! command -v serverless &> /dev/null; then
    echo -e "${YELLOW}Installing Serverless Framework...${NC}"
    npm install -g serverless
fi

# Check if AWS CLI is configured
if ! aws sts get-caller-identity &> /dev/null; then
    echo -e "${RED}Error: AWS CLI not configured. Please run 'aws configure' first.${NC}"
    exit 1
fi

# Get stage from argument or default to dev
STAGE=${1:-dev}
echo -e "${BLUE}Deploying to stage: ${STAGE}${NC}"

# Install Node.js dependencies
echo -e "${YELLOW}Installing Node.js dependencies...${NC}"
npm install

# Install Python dependencies for Lambda
echo -e "${YELLOW}Installing Python dependencies for Lambda...${NC}"
pip install -r lambda_requirements.txt -t ./

# Deploy to AWS Lambda
echo -e "${YELLOW}Deploying to AWS Lambda...${NC}"
serverless deploy --stage $STAGE --verbose

# Get the API Gateway URL
echo -e "${GREEN}Deployment completed!${NC}"
echo -e "${BLUE}Getting API Gateway URL...${NC}"

API_URL=$(serverless info --stage $STAGE | grep -o 'https://[^/]*\.execute-api\.[^/]*\.amazonaws\.com/[^/]*')

if [ ! -z "$API_URL" ]; then
    echo -e "${GREEN}🎉 API deployed successfully!${NC}"
    echo -e "${BLUE}API URL: ${API_URL}${NC}"
    echo -e "${BLUE}Health Check: ${API_URL}/health${NC}"
    echo -e "${BLUE}API Docs: ${API_URL}/docs${NC}"
    echo -e "${BLUE}Caption Extract: ${API_URL}/api/v1/captions/extract${NC}"
    
    # Test the deployment
    echo -e "${YELLOW}Testing deployment...${NC}"
    curl -s "${API_URL}/health" | jq '.' || echo "Health check failed"
else
    echo -e "${RED}Failed to get API URL${NC}"
fi

echo -e "${GREEN}Deployment script completed!${NC}"
