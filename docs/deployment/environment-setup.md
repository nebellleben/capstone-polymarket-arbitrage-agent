# Environment Variables Setup Guide

This document explains all environment variables required for the Polymarket Arbitrage Agent MVP.

## Quick Setup

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` with your API keys

3. Source the environment:
   ```bash
   source .env  # Linux/Mac
   # or
   set -a; source .env; set +a  # Some shells
   ```

## Required Environment Variables

### Brave Search API Key

**Variable**: `BRAVE_API_KEY`
**Required**: ✅ Yes (for live news, otherwise mock data)
**Description**: API key for Brave Search to fetch news articles
**How to Get**:
1. Go to [Brave Search API](https://api.search.brave.com/app/keys)
2. Sign up for a free account
3. Create an API key
4. Copy the key

**Example**:
```bash
BRAVE_API_KEY=BSAz7j5xN1fM...
```

**Testing**: Without this key, the system will use mock news data for testing.

### Anthropic API Key

**Variable**: `ANTHROPIC_API_KEY`
**Required**: ✅ Yes (for AI reasoning, otherwise fallback)
**Description**: API key for Anthropic Claude API used in reasoning client
**How to Get**:
1. Go to [Anthropic Console](https://console.anthropic.com/)
2. Sign up or log in
3. Go to API Keys
4. Create a new API key
5. Copy the key

**Example**:
```bash
ANTHROPIC_API_KEY=sk-ant-...
```

**Testing**: Without this key, the system will use keyword-based fallback reasoning.

## Optional Environment Variables

### Application Settings

#### ENVIRONMENT
- **Default**: `development`
- **Values**: `development`, `production`
- **Description**: Application environment
- **Production**: Set to `production`

```bash
ENVIRONMENT=production
```

#### LOG_LEVEL
- **Default**: `INFO`
- **Values**: `DEBUG`, `INFO`, `WARNING`, `ERROR`
- **Description**: Logging verbosity level
- **Production**: Use `INFO` or `WARNING`

```bash
LOG_LEVEL=INFO
```

### News Monitoring

#### SEARCH_QUERIES
- **Default**: `breaking news politics`
- **Description**: Comma-separated list of search queries for news monitoring

```bash
SEARCH_QUERIES="breaking news politics,crypto news,election updates,stock market"
```

#### NEWS_SEARCH_INTERVAL
- **Default**: `60`
- **Description**: Seconds between news search cycles
- **Range**: 30-3600

```bash
NEWS_SEARCH_INTERVAL=60  # Search every minute
```

#### NEWS_MAX_RESULTS
- **Default**: `10`
- **Description**: Maximum news articles to fetch per search
- **Range**: 1-50

```bash
NEWS_MAX_RESULTS=20
```

#### NEWS_FRESHNESS
- **Default**: `pd`
- **Values**: `pd` (day), `pw` (week), `pm` (month)
- **Description**: News freshness filter

```bash
NEWS_FRESHNESS=pd  # Past 24 hours
```

### Market Data

#### POLYMARKET_GAMMA_HOST
- **Default**: `gamma-api.polymarket.com`
- **Description**: Polymarket Gamma API host

```bash
POLYMARKET_GAMMA_HOST=gamma-api.polymarket.com
```

#### MARKET_REFRESH_INTERVAL
- **Default**: `300` (5 minutes)
- **Description**: Seconds between market data refreshes
- **Range**: 60-3600

```bash
MARKET_REFRESH_INTERVAL=300  # Refresh every 5 minutes
```

#### POLYMARKET_TIMEOUT
- **Default**: `30`
- **Description**: API request timeout in seconds
- **Range**: 10-120

```bash
POLYMARKET_TIMEOUT=30
```

#### POLYMARKET_RATE_LIMIT
- **Default**: `10`
- **Description**: API rate limit (requests per second)
- **Range**: 1-100

```bash
POLYMARKET_RATE_LIMIT=10
```

### Arbitrage Detection

#### CONFIDENCE_THRESHOLD
- **Default**: `0.7`
- **Description**: Minimum confidence level for generating alerts (0.0-1.0)
- **Range**: 0.5-1.0

```bash
CONFIDENCE_THRESHOLD=0.7  # Only alert on 70%+ confidence
```

#### MIN_PROFIT_MARGIN
- **Default**: `0.05`
- **Description**: Minimum price discrepancy for alerts (0.05 = 5%)
- **Range**: 0.01-0.5

```bash
MIN_PROFIT_MARGIN=0.05  # Require 5% profit margin
```

#### RELEVANCE_THRESHOLD
- **Default**: `0.5`
- **Description**: Minimum news-market relevance to analyze (0.0-1.0)
- **Range**: 0.0-1.0

```bash
RELEVANCE_THRESHOLD=0.5  # Only analyze if 50%+ relevant
```

### Alerting

#### ALERT_RETENTION
- **Default**: `100`
- **Description**: Number of alerts to retain in memory
- **Range**: 10-1000

```bash
ALERT_RETENTION=100  # Keep last 100 alerts
```

#### ALERT_COOLDOWN
- **Default**: `300` (5 minutes)
- **Description**: Minimum seconds between alerts for same market
- **Range**: 60-3600

```bash
ALERT_COOLDOWN=300  # Don't alert same market within 5 minutes
```

### Cache Settings

#### MARKET_CACHE_TTL
- **Default**: `300` (5 minutes)
- **Description**: Market cache TTL in seconds

```bash
MARKET_CACHE_TTL=300
```

#### NEWS_CACHE_TTL
- **Default**: `86400` (24 hours)
- **Description**: News cache TTL in seconds

```bash
NEWS_CACHE_TTL=86400
```

## Docker Environment

When using Docker, pass environment variables via:

### Docker Run
```bash
docker run -e BRAVE_API_KEY="$BRAVE_API_KEY" ...
```

### Docker Compose
Set in `docker-compose.yml`:
```yaml
environment:
  - BRAVE_API_KEY=${BRAVE_API_KEY}
```

### Railway
Set in Railway Dashboard → Variables

### Render
Set in Render Dashboard → Environment

## GitHub Secrets (for CI/CD)

Set these in GitHub Repository Settings → Secrets:

### Required
- `BRAVE_API_KEY`: Your Brave Search API key
- `ANTHROPIC_API_KEY`: Your Anthropic API key
- `RAILWAY_TOKEN`: Railway CLI token (if deploying to Railway)
- `RAILWAY_SERVICE_ID`: Railway service ID
- `RENDER_SERVICE_ID`: Render service ID (if deploying to Render)

### Optional
- `SLACK_WEBHOOK`: Slack webhook for deployment notifications
- `CODECOV_TOKEN`: Codecov token for coverage reports

## Verification

### Test Environment Variables
```bash
# Check if variables are set
echo $BRAVE_API_KEY
echo $ANTHROPIC_API_KEY

# Or use the Python script
python -c "from src.utils.config import settings; print(settings.brave_api_key)"
```

### Load .env File
```bash
# Using python-dotenv
python -c "from dotenv import load_dotenv; load_dotenv(); import os; print(os.getenv('BRAVE_API_KEY'))"
```

## Troubleshooting

### Issue: API Key Not Recognized

**Symptom**: System uses mock data instead of real API

**Solution**:
1. Verify variable is set: `echo $BRAVE_API_KEY`
2. Check for spaces: Ensure no quotes or spaces around key
3. Restart application: Environment variables loaded at startup

### Issue: Environment Variables Not Loaded in Docker

**Symptom**: Container crashes with missing variable error

**Solution**:
```bash
# Explicitly pass environment variables
docker run -e BRAVE_API_KEY="$BRAVE_API_KEY" ...

# Or use --env-file
docker run --env-file .env ...
```

### Issue: Different Values in Different Environments

**Symptom**: Variable works locally but not in production

**Solution**:
- Check for trailing spaces in `.env` file
- Verify variable name matches exactly (case-sensitive)
- Ensure `.env` is in the correct directory

## Security Best Practices

### ✅ DO
- Store API keys in environment variables only
- Never commit `.env` file to Git
- Use different keys for dev/staging/production
- Rotate keys regularly
- Use read-only keys when possible
- Set appropriate permissions: `chmod 600 .env`

### ❌ DON'T
- Hardcode API keys in source code
- Commit `.env` to version control
- Share keys via email/chat
- Use production keys in development
- Log or print API keys
- Include keys in error messages

## Production Configuration

### Recommended Production Settings

```bash
# Application
ENVIRONMENT=production
LOG_LEVEL=WARNING

# Detection (stricter)
CONFIDENCE_THRESHOLD=0.8
MIN_PROFIT_MARGIN=0.10
RELEVANCE_THRESHOLD=0.6

# Intervals (reduced for cost)
NEWS_SEARCH_INTERVAL=120
MARKET_REFRESH_INTERVAL=600

# Rate limiting
POLYMARKET_RATE_LIMIT=5

# Retention
ALERT_RETENTION=50
```

## Support

For issues with environment variables:

1. Check this documentation
2. Review `.env.example` for all variables
3. Check application logs for specific errors
4. Open a GitHub issue

---

**Last Updated**: 2025-01-12
**Maintained By**: DevOps Engineer Agent
