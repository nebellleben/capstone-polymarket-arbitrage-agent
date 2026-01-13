# Railway Deployment Guide

## ✅ Deployment Status: **LIVE**

**Production URL**: https://capstone-polymarket-arbitrage-agent-production.up.railway.app/

**Status**: ✅ Fully Operational (Deployed: 2026-01-13)
- Health checks passing
- Worker running detection cycles
- Database connected
- API endpoints accessible

## Quick Start

1. **Install Railway CLI**
   ```bash
   npm install -g @railway/cli
   ```

2. **Login to Railway**
   ```bash
   railway login
   ```

3. **Create Project**
   ```bash
   railway init
   ```

4. **Set Environment Variables**
   ```bash
   railway variables set BRAVE_API_KEY=your_key_here
   railway variables set ANTHROPIC_API_KEY=your_key_here
   railway variables set ENVIRONMENT=production
   railway variables set LOG_LEVEL=INFO
   railway variables set CONFIDENCE_THRESHOLD=0.7
   railway variables set MIN_PROFIT_MARGIN=0.05
   ```

5. **Deploy**
   ```bash
   railway up
   ```

## Railway Service Configuration

### ⚠️ CRITICAL: Port Configuration

**You MUST set the Port in Railway service Settings:**

1. Go to Railway dashboard
2. Open service → **Settings** tab
3. Find **Port** field
4. Set it to: **`8080`**
5. Save and redeploy

**Why This is Required**:
- The Dockerfile has `EXPOSE 8080` directive
- The application binds to `0.0.0.0:8080` inside the container
- But Railway's Edge Proxy needs to know which port to forward traffic to
- Without this setting, you'll get HTTP 502 "Application failed to respond"

### Service Type: Dockerfile

### Build Settings
- **Dockerfile Path**: `Dockerfile`
- **Context**: `/`
- **Port**: `8080` (set in Settings tab)

### Environment Variables Required

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `BRAVE_API_KEY` | Brave Search API key | Yes | - |
| `ANTHROPIC_API_KEY` | Anthropic API key | Yes | - |
| `ENVIRONMENT` | Environment | No | `production` |
| `LOG_LEVEL` | Logging level | No | `INFO` |
| `CONFIDENCE_THRESHOLD` | Min confidence for alerts | No | `0.7` |
| `MIN_PROFIT_MARGIN` | Min profit margin | No | `0.05` |
| `SEARCH_QUERIES` | News search queries | No | `breaking news politics` |
| `NEWS_SEARCH_INTERVAL` | Seconds between searches | No | `60` |
| `MARKET_REFRESH_INTERVAL` | Seconds between market refreshes | No | `300` |

### Resource Allocation

**Recommended for MVP**:
- **CPU**: 0.5 vCPU
- **RAM**: 512 MB
- **Cost**: ~$5-10/month

**For Production**:
- **CPU**: 1-2 vCPU
- **RAM**: 1-2 GB
- **Cost**: ~$20-30/month

## Deployment Strategy

### Automatic Deployment
Railway automatically deploys when you push to the connected branch.

### Health Check
The container includes a health check that runs every 30 seconds.

### Logs
View logs in Railway dashboard:
```bash
railway logs
```

## Troubleshooting

### Container Not Starting
1. Check build logs: `railway logs`
2. Verify environment variables: `railway variables list`
3. Check resources: Ensure enough RAM allocated

### Application Crashes
1. View logs: `railway logs --tail`
2. Common issues:
   - Missing API keys
   - Insufficient memory
   - API rate limits

## Monitoring

Railway provides basic metrics:
- CPU usage
- Memory usage
- Network traffic
- Restart count

Access via Railway Dashboard.

## Verification

After deployment, verify the application is working:

```bash
# Test health endpoint
curl https://your-app.up.railway.app/api/health

# Expected response:
# {"status":"healthy","timestamp":"..."}
```

**Available Endpoints**:
- `/` - API information
- `/api/health` - Health check
- `/api/status` - System status (worker, database)
- `/api/alerts` - List alerts
- `/api/alerts/recent` - Recent alerts
- `/api/alerts/stats` - Alert statistics
- `/api/metrics` - Performance metrics
- `/api/docs` - Interactive Swagger documentation

## Deployment Success Story

**Deployment Date**: 2026-01-13

**What Works**:
- ✅ Container starts successfully
- ✅ Health endpoint returns HTTP 200
- ✅ Database connected and operational
- ✅ Background worker running detection cycles
- ✅ API endpoints accessible
- ✅ Real-time monitoring via dashboard

**Key Configuration**:
- Dockerfile with `EXPOSE 8080` directive
- Railway service Port set to `8080`
- PORT variable auto-injected by Railway
- Application binds to `0.0.0.0:8080`

**Production URL**: https://capstone-polymarket-arbitrage-agent-production.up.railway.app/

See Also:
- `docs/deployment/deployment-verification-guide.md` - Detailed verification steps
- `docs/deployment/troubleshooting-railway-502.md` - Troubleshooting guide
- `docs/security/security-report-mvp.md` - Security review
