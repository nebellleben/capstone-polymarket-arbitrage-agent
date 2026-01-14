#!/bin/bash

# Railway Deployment Script
# This script automates deployment to Railway

set -e  # Exit on error

echo "=== Railway Deployment Script ==="
echo ""

# Check if logged in to Railway
echo "Step 1: Checking Railway login status..."
if ! railway status &>/dev/null; then
    echo "❌ Not logged in to Railway"
    echo "Please run: railway login"
    echo "Then re-run this script"
    exit 1
fi

echo "✓ Logged in to Railway"
echo ""

# Load environment variables
echo "Step 2: Loading environment variables..."
if [ ! -f .env ]; then
    echo "❌ .env file not found"
    exit 1
fi

source .env

# Verify required variables
echo "Step 3: Verifying required API keys..."
required_vars=("BRAVE_API_KEY" "ANTHROPIC_API_KEY" "POLYMARKET_API_KEY")
missing_vars=()

for var in "${required_vars[@]}"; do
    if [ -z "${!var}" ]; then
        missing_vars+=("$var")
    fi
done

if [ ${#missing_vars[@]} -gt 0 ]; then
    echo "❌ Missing required variables: ${missing_vars[*]}"
    exit 1
fi

echo "✓ All required API keys are set"
echo ""

# Link or initialize Railway project
echo "Step 4: Checking Railway project..."
if ! railway status &>/dev/null; then
    echo "No project linked. Creating new project..."
    railway init
else
    echo "✓ Project already linked"
fi
echo ""

# Set environment variables
echo "Step 5: Uploading environment variables to Railway..."
railway variables set BRAVE_API_KEY="$BRAVE_API_KEY"
railway variables set ANTHROPIC_API_KEY="$ANTHROPIC_API_KEY"
railway variables set POLYMARKET_API_KEY="$POLYMARKET_API_KEY"
railway variables set POLYMARKET_SECRET_KEY="$POLYMARKET_SECRET_KEY"

if [ -n "$TELEGRAM_BOT_TOKEN" ]; then
    railway variables set TELEGRAM_BOT_TOKEN="$TELEGRAM_BOT_TOKEN"
    railway variables set TELEGRAM_CHAT_ID="$TELEGRAM_CHAT_ID"
    railway variables set TELEGRAM_ENABLED="true"
fi

railway variables set LOG_LEVEL="INFO"
railway variables set ENVIRONMENT="production"
railway variables set CONFIDENCE_THRESHOLD="0.7"
railway variables set MIN_PROFIT_MARGIN="0.05"

echo "✓ Environment variables uploaded"
echo ""

# Deploy to Railway
echo "Step 6: Deploying to Railway..."
echo "This may take a few minutes..."
railway up

echo ""
echo "✓ Deployment initiated!"
echo ""

# Get service URL
echo "Step 7: Getting service URL..."
sleep 5
SERVICE_URL=$(railway domain --json 2>/dev/null | grep -o '"url":"[^"]*"' | cut -d'"' -f4 | head -1)

if [ -n "$SERVICE_URL" ]; then
    echo "✓ Service deployed at: $SERVICE_URL"
    echo ""
    echo "Dashboard: $SERVICE_URL"
    echo "Health Check: $SERVICE_URL/api/health"
    echo "API Docs: $SERVICE_URL/api/docs"
else
    echo "⚠️  Service URL not ready yet"
    echo "Check: railway status"
fi

echo ""
echo "=== Deployment Complete ==="
echo ""
echo "Next steps:"
echo "1. Monitor logs: railway logs --tail"
echo "2. Check status: railway status"
echo "3. View metrics: railway metrics"
echo ""
