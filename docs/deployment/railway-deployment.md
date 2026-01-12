# Deployment Configuration for Railway

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

### Service Type: Dockerfile

### Build Settings
- **Dockerfile Path**: `Dockerfile`
- **Context**: `/`

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
