# Deployment Configuration for Render

## Quick Start

### Via Dashboard

1. **Create New Web Service**
   - Go to [render.com](https://render.com)
   - Click "New" → "Web Service"
   - Connect your GitHub repository

2. **Configure Build**
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python -m src.workflows.mvp_workflow`

3. **Set Environment Variables**
   - Add all required variables (see below)
   - Click "Save"

4. **Deploy**
   - Click "Create Web Service"
   - Render will auto-deploy on push

### Via Render CLI

1. **Install Render CLI**
   ```bash
   npm install -g @render/cli
   ```

2. **Initialize**
   ```bash
   render init
   ```

3. **Deploy**
   ```bash
   render deploy
   ```

## render.yaml Specification

Create `render.yaml` in repository root:

```yaml
services:
  # Type: Web Service
  - type: web
    name: polymarket-arbitrage-agent
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: python -m src.workflows.mvp_workflow

    # Auto-deploy on push to main branch
    branch: main

    # Environment Variables (set in dashboard, not here for security)
    envVars:
      - key: ENVIRONMENT
        value: production
      - key: LOG_LEVEL
        value: INFO
      - key: CONFIDENCE_THRESHOLD
        value: 0.7
      - key: MIN_PROFIT_MARGIN
        value: 0.05

    # Resource Limits
    plan: starter  # or pro for production

    # Health Check
    healthCheckPath: /

    # Disk
    disk:
      name: data
      mountPath: /app/data
      sizeGB: 1
```

## Environment Variables

Set these in Render Dashboard (Environment tab):

### Required
- `BRAVE_API_KEY`: Your Brave Search API key
- `ANTHROPIC_API_KEY`: Your Anthropic API key

### Optional (with defaults)
- `ENVIRONMENT`: `production`
- `LOG_LEVEL`: `INFO`
- `CONFIDENCE_THRESHOLD`: `0.7`
- `MIN_PROFIT_MARGIN`: `0.05`
- `SEARCH_QUERIES`: `breaking news politics`
- `NEWS_SEARCH_INTERVAL`: `60`
- `MARKET_REFRESH_INTERVAL`: `300`
- `POLYMARKET_GAMMA_HOST`: `gamma-api.polymarket.com`
- `POLYMARKET_TIMEOUT`: `30`
- `POLYMARKET_RATE_LIMIT`: `10`

## Resource Plans

### Free Tier ($0)
- **CPU**: 0.1 vCPU (shared)
- **RAM**: 512 MB
- **Sleeps after 15 min inactivity**
- ❌ Not suitable for 24/7 monitoring

### Starter ($7/month)
- **CPU**: 0.5 vCPU
- **RAM**: 512 MB
- ✅ Always running
- ✅ Good for MVP testing

### Pro ($25/month)
- **CPU**: 2 vCPU
- **RAM**: 4 GB
- ✅ Production ready
- ✅ Better performance

## Deployment Strategy

### Automatic Deployment
Render auto-deploys when you push to the connected branch (main).

### Manual Deployment
Click "Manual Deploy" in the Render dashboard.

### Zero-Downtime Deployments
Render supports zero-downtime deployments automatically.

## Health Checks

### Default Health Check
Render checks if the service is responding every 30 seconds.

### Custom Health Check
Add a health check endpoint in future:
```python
# In main workflow
from fastapi import FastAPI
app = FastAPI()

@app.get("/health")
async def health():
    return {"status": "healthy"}
```

Update start command:
```
gunicorn -w 1 -k uvicorn.workers.UvicornWorker main:app
```

## Monitoring

### Render Dashboard
- **Metrics**: CPU, Memory, Network
- **Logs**: Real-time logs
- **Events**: Deployments, restarts

### Log Streaming
```bash
# Via CLI
render logs -f polymarket-arbitrage-agent
```

## Troubleshooting

### Service Not Starting

1. **Check Logs**: View logs in dashboard
2. **Build Failures**: Check build tab for errors
3. **Missing Dependencies**: Verify requirements.txt

### Runtime Errors

1. **View Logs**: Real-time log streaming
2. **Environment Variables**: Verify all set correctly
3. **API Keys**: Check keys are valid

### Performance Issues

1. **Upgrade Plan**: Move to Starter/Pro
2. **Check Logs**: Look for rate limiting
3. **Optimize**: Reduce search frequency

## Background Jobs

For continuous monitoring, use **Render Cron Jobs**:

```yaml
# In render.yaml
- type: cron
  name: arbitrage-monitor
  schedule: "0 * * * *"  # Every hour
  env: python
  buildCommand: pip install -r requirements.txt
  startCommand: python -m src.workflows.mvp_workflow
```

## Cost Optimization

### Development
- Use Free Tier
- Manually start when needed
- Set longer sleep intervals

### Production
- Use Starter Plan ($7/month)
- Monitor usage
- Scale up only if needed

## Backup and Restore

### Data Persistence

Render provides ephemeral disk storage. For persistence:

1. **Use Render Disk** (add to render.yaml)
2. **External Database** (add PostgreSQL)
3. **Object Storage** (add AWS S3)

### Automated Backups

Configure in Render Dashboard → Services → Your Service → Settings

## Comparison: Railway vs Render

| Feature | Railway | Render |
|---------|---------|--------|
| Free Tier | ❌ No | ✅ Yes ($0, with sleep) |
| Always On | ✅ Yes (from $5/mo) | ❌ No (on free tier) |
| CLI | ✅ Yes | ✅ Yes |
| Auto-Deploy | ✅ Yes | ✅ Yes |
| Zero-Downtime | ✅ Yes | ✅ Yes |
| Cron Jobs | ❌ No | ✅ Yes |
| Disk Storage | ✅ Yes | ✅ Yes |

**Recommendation**: Use **Railway** for always-on MVP testing ($5-10/mo).
