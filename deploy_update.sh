#!/bin/bash

# Allervie Analytics Dashboard Deployment Script
# This script helps to deploy the Allervie Analytics Dashboard to DigitalOcean App Platform

# Check if doctl is installed
if ! command -v doctl &> /dev/null; then
    echo "Error: doctl is not installed."
    echo "Please install the DigitalOcean CLI tool by following the instructions at:"
    echo "https://docs.digitalocean.com/reference/doctl/how-to/install/"
    exit 1
fi

# Check if user is authenticated with doctl
if ! doctl account get &> /dev/null; then
    echo "You need to authenticate with DigitalOcean."
    echo "Run 'doctl auth init' and follow the prompts."
    exit 1
fi

# Create the app
echo "Creating the DigitalOcean app from the YAML configuration..."
APP_ID=$(doctl apps update 9f14d323-8b99-46d8-9467-55b491ddfdea --spec app.yaml --format ID --no-header)

if [ -z "$APP_ID" ]; then
    echo "Error: Failed to create app or retrieve app ID."
    exit 1
fi

echo "Successfully created app with ID: $APP_ID"
echo "You can view your app deployment status by running:"
echo "doctl apps get $APP_ID"

echo ""
echo "IMPORTANT: Once deployment is complete, you need to set up the following environment secrets:"
echo "- GOOGLE_ADS_CLIENT_SECRET"
echo "- GOOGLE_ADS_DEVELOPER_TOKEN"
echo "- GOOGLE_ADS_REFRESH_TOKEN"
echo ""
echo "You can do this from the DigitalOcean App Platform dashboard or with the following commands:"
echo "doctl apps update $APP_ID --spec app.yaml"
echo ""
echo "For security reasons, this script does not include sensitive credentials."
echo "Please update these values manually in the DigitalOcean dashboard or the app.yaml file."

# Get app URL
echo "Checking deployment status..."
sleep 10 # Wait a short time for the deployment to start
APP_URL=$(doctl apps get $APP_ID --format DefaultIngress --no-header)

if [ -n "$APP_URL" ]; then
    echo "Your app will be available at: $APP_URL"
    echo "It may take a few minutes for the deployment to complete."
else
    echo "App created, but could not retrieve the URL yet."
    echo "Check deployment status with: doctl apps get $APP_ID"
fi