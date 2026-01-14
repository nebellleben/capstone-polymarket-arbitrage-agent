# Railway Deployment Guide

## Prerequisites

✅ All required API keys are configured in `.env`:
- BRAVE_API_KEY ✓
- ANTHROPIC_API_KEY ✓
- POLYMARKET_API_KEY ✓
- TELEGRAM_BOT_TOKEN ✓
- TELEGRAM_CHAT_ID ✓

## Deployment Steps

### Step 1: Login to Railway (Interactive)

Open a terminal and run:
```bash
railway login
```

This will open your browser for authentication.

### Step 2: Link/Create Railway Project

```bash
# Option A: Link to existing project
railway link

# Option B: Create new project
railway init
```

### Step 3: Upload Environment Variables

```bash
# Set required environment variables
railway variables set BRAVE_API_KEY="$BRAVE_API_KEY"
railway variables set ANTHROPIC_API_KEY="$ANTHROPIC_API_KEY"
railway variables set POLYMARKET_API_KEY="$POLYMARKET_API_KEY"
railway variables set POLYMARKET_SECRET_KEY="$POLYMARKET_SECRET_KEY"

# Set optional Telegram variables
railway variables set TELEGRAM_BOT_TOKEN="$TELEGRAM_BOT_TOKEN"
railway variables set TELEGRAM_CHAT_ID="$TELEGRAM_CHAT_ID"
railway variables set TELEGRAM_ENABLED="true"

# Set application settings
railway variables set LOG_LEVEL="INFO"
railway variables set ENVIRONMENT="production"
railway variables set CONFIDENCE_THRESHOLD="0.7"
railway variables set MIN_PROFIT_MARGIN="0.05"

# Verify variables
railway variables
```

### Step 4: Deploy to Railway

```bash
# Deploy the service
railway up

# Monitor deployment logs
railway logs

# Check service status
railway status
```

### Step 5: Access Your Dashboard

Once deployed, Railway will provide:
- **Dashboard URL**: https://your-project.railway.app/
- **Health Check**: https://your-project.railway.app/api/health
- **API Docs**: https://your-project.railway.app/api/docs

### Step 6: Monitor the Service

```bash
# View live logs
railway logs --tail

# Check metrics
railway metrics

# View status
railway status
```

## What Happens During Deployment

1. **Build**: Docker container is built
2. **Deploy**: Container is deployed to Railway infrastructure
3. **Start**: Both services start automatically:
   - **Detection Worker**: Continuously monitors news and detects arbitrage
   - **Web API**: Serves dashboard and REST API

## Verification

### Check Worker is Running

```bash
# View logs for detection activity
railway logs --tail | grep "search_news\|detect_opportunities\|alert_created"
```

### Check Web Server

```bash
# Health check
curl https://your-project.railway.app/api/health

# Check recent alerts
curl https://your-project.railway.app/api/alerts/recent?limit=5
```

### Access Dashboard

Open your browser and navigate to your Railway URL.

## Troubleshooting

### Logs Show API Errors

```bash
# Check if variables are set correctly
railway variables get BRAVE_API_KEY
railway variables get ANTHROPIC_API_KEY
```

### Service Not Starting

```bash
# Check deployment status
railway status

# View error logs
railway logs --tail
```

### Database Issues

The system automatically initializes SQLite database at `/app/data/arbitrage.db`.

## Local Testing

Before deploying, test locally:

```bash
# Start services locally
bash docker-entrypoint.sh

# Or run separately:
# Terminal 1: Start worker
python -m src.workflows.mvp_workflow

# Terminal 2: Start web server
uvicorn src.api.main:app --host 0.0.0.0 --port 8000
```

## Cost Monitoring

```bash
# Check current usage
railway balance

# View metrics
railway metrics
```

## Support

- Railway Documentation: https://docs.railway.app/
- Project Dashboard: https://railway.app/project
- Troubleshooting: `railway help`
