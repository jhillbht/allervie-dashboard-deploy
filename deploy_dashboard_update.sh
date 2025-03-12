#!/bin/bash

# Deploy script for updating the Allervie dashboard

# Terminal colors
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Allervie Dashboard Update Deployment${NC}"
echo -e "${BLUE}========================================${NC}"

# Check if environment variables are set
if [ -z "$GOOGLE_ADS_CLIENT_ID" ] || [ -z "$GOOGLE_ADS_CLIENT_SECRET" ] || [ -z "$GOOGLE_ADS_DEVELOPER_TOKEN" ] || [ -z "$GOOGLE_ADS_LOGIN_CUSTOMER_ID" ] || [ -z "$GOOGLE_ADS_REFRESH_TOKEN" ]; then
    echo -e "${YELLOW}Warning: Some Google Ads API environment variables are not set.${NC}"
    echo -e "${YELLOW}The dashboard will use mock data instead of real Google Ads data.${NC}"
    echo -e "${YELLOW}To use real data, set the following environment variables:${NC}"
    echo -e "${YELLOW}- GOOGLE_ADS_CLIENT_ID${NC}"
    echo -e "${YELLOW}- GOOGLE_ADS_CLIENT_SECRET${NC}"
    echo -e "${YELLOW}- GOOGLE_ADS_DEVELOPER_TOKEN${NC}"
    echo -e "${YELLOW}- GOOGLE_ADS_LOGIN_CUSTOMER_ID${NC}"
    echo -e "${YELLOW}- GOOGLE_ADS_REFRESH_TOKEN${NC}"
    echo ""
    echo -e "${YELLOW}Continue with deployment? (y/n)${NC}"
    read -r response
    if [[ "$response" != "y" ]]; then
        echo -e "${RED}Deployment cancelled.${NC}"
        exit 1
    fi
fi

# Check if dashboard.py exists
if [ ! -f "dashboard.py" ]; then
    echo -e "${RED}Error: dashboard.py file not found.${NC}"
    echo -e "${RED}Make sure you are running this script from the deployment directory.${NC}"
    exit 1
fi

# Stop any running server process
echo -e "${BLUE}Stopping any running dashboard process...${NC}"
pkill -f "python dashboard.py" || true
echo -e "${GREEN}Server stopped or not running.${NC}"

# Start the server
echo -e "${BLUE}Starting Allervie dashboard...${NC}"
nohup python dashboard.py > dashboard.log 2>&1 &
SERVER_PID=$!

# Wait a moment to ensure the server starts
sleep 2

# Check if the server started successfully
if ps -p $SERVER_PID > /dev/null; then
    echo -e "${GREEN}Dashboard successfully started!${NC}"
    echo -e "${GREEN}Process ID: ${SERVER_PID}${NC}"
    echo -e "${GREEN}Dashboard URL: http://localhost:8080/ads-dashboard${NC}"
    echo -e "${GREEN}Log file: dashboard.log${NC}"
else
    echo -e "${RED}Failed to start the dashboard.${NC}"
    echo -e "${RED}Check dashboard.log for details.${NC}"
    exit 1
fi

echo -e "${BLUE}========================================${NC}"
echo -e "${GREEN}Deployment complete!${NC}"
echo -e "${BLUE}========================================${NC}"