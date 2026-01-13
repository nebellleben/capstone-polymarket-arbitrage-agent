#!/bin/bash

# Railway Diagnostic Script
# Tests if the Railway deployment is accessible on different ports

echo "Testing Railway deployment accessibility..."
echo ""
echo "Deployment URL: https://capstone-polymarket-arbitrage-agent-production.up.railway.app/"
echo ""
echo "Testing various endpoints:"
echo ""

# Test health endpoint
echo "1. Testing /api/health endpoint..."
curl -s -w "HTTP Status: %{http_code}\n" https://capstone-polymarket-arbitrage-agent-production.up.railway.app/api/health
echo ""

# Test root endpoint
echo "2. Testing / endpoint..."
curl -s -w "HTTP Status: %{http_code}\n" https://capstone-polymarket-arbitrage-agent-production.up.railway.app/
echo ""

# Test status endpoint
echo "3. Testing /api/status endpoint..."
curl -s -w "HTTP Status: %{http_code}\n" https://capstone-polymarket-arbitrage-agent-production.up.railway.app/api/status
echo ""

echo "========================================="
echo ""
echo "If all tests return 502, the issue is likely:"
echo "1. Railway service 'Port' setting is not configured"
echo "2. Railway's proxy doesn't know which port to forward to"
echo ""
echo "TO FIX:"
echo "1. Go to Railway dashboard"
echo "2. Open service → Settings"
echo "3. Find 'Port' or 'Listening Port' field"
echo "4. Set it to: 8080"
echo "5. Save and redeploy"
echo ""
