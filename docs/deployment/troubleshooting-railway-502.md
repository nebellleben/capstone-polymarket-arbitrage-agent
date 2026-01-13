# Troubleshooting Railway 502 Errors

## Current Status
- **All code fixes pushed to GitHub**: ✅ Complete
- **Railway deployment URL**: https://capstone-polymarket-arbitrage-agent-production.up.railway.app/
- **Current error**: HTTP 502 "Application failed to respond"

---

## Most Likely Cause: Railway Hasn't Rebuilt Yet

Railway may not be connected to GitHub for automatic deployments. You need to either:

### Option 1: Connect Railway to GitHub (Recommended)

1. Go to https://railway.app/
2. Open your project: `capstone-polymarket-arbitrage-agent`
3. Click on your service
4. Go to **Settings** → **GitHub**
5. Click **Connect GitHub**
6. Select the repository: `nebellleben/capstone-polymarket-arbitrage-agent`
7. Select branch: `main`
8. Railway will now auto-deploy on every push

### Option 2: Manual Deploy via Railway Dashboard

1. Go to https://railway.app/
2. Open your project
3. Click on the service
4. Click **New Deployment** button
5. Railway will rebuild with latest code from GitHub

### Option 3: Manual Deploy via Railway CLI

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login to Railway
railway login

# Select your project
railway project

# Trigger deployment
railway up

# Monitor logs
railway logs
```

---

## Verification Steps After Redeploy

### 1. Check Build Logs
In Railway dashboard, watch for:
- ✅ "Successfully built image"
- ✅ "Deploying new version..."
- ❌ Look for any build errors

### 2. Check Deployment Logs
After deploy, click on the deployment and view logs. You should see:
```
=== Starting Polymarket Arbitrage Agent ===
Environment: production
PWD: /app
Railway PORT: <some_port>
Web Server Port: <same_port>
=========================================
Initializing database...
✓ Database initialized successfully
Starting detection worker...
Starting web server on port <port>...
✓ Services started successfully
  - Worker PID: X
  - Web Server PID: Y
  - Health check: http://localhost:<port>/api/health
```

### 3. Test Health Endpoint
```bash
curl https://capstone-polymarket-arbitrage-agent-production.up.railway.app/api/health
```

Expected: HTTP 200 with response:
```json
{"status":"healthy","timestamp":"2026-01-13T..."}
```

---

## If Still Getting 502 After Redeploy

### Check Railway Environment Variables

In Railway dashboard: **Settings** → **Variables**

Verify these are set:
```
LOG_LEVEL=INFO
ENVIRONMENT=production
PORT=8080
HEALTHCHECK_PATH=/api/health
```

Optional (for news monitoring):
```
BRAVE_API_KEY=your_key_here
ANTHROPIC_API_KEY=your_key_here
```

### Check Railway Service Configuration

In Railway dashboard: **Settings** tab

Verify:
- **Root Directory**: `.` (or empty)
- **Dockerfile path**: `Dockerfile`
- **Healthcheck Path**: `/api/health`

### Check if Port is Correctly Set

The application uses Railway's PORT environment variable. Verify in the logs:
```
Railway PORT: 8080  (or some other port)
Web Server Port: 8080 (should match Railway PORT)
```

---

## Alternative: Test Locally with Docker

To verify the fixes work correctly:

```bash
# Build image
docker build -t arbitrage-test .

# Run with Railway-like environment
docker run -p 8080:8080 \
  -e PORT=8080 \
  -e ENVIRONMENT=production \
  arbitrage-test

# In another terminal, test health
curl http://localhost:8080/api/health
```

Expected: HTTP 200 OK

---

## Common Issues and Solutions

### Issue: "Port already in use"
**Solution**: Railway assigns ports automatically, ensure app uses PORT env var

### Issue: "Database initialization failed"
**Solution**: Check permissions, ensure /app/data directory exists

### Issue: "Import error"
**Solution**: Verify requirements.txt installed correctly

### Issue: "Container keeps restarting"
**Solution**: Check logs for crash reason, likely startup failure

---

## Local Testing Worked!

Our local Docker test was successful:
```
✓ Database initialized successfully
✓ Services started successfully
  - Worker PID: 8
  - Web Server PID: 9
  - Health check: http://localhost:8080/api/health

$ curl http://localhost:8080/api/health
{"status":"healthy","timestamp":"2026-01-12T17:29:43.050584"}
HTTP 200 OK
```

This confirms the code and configuration are correct. The issue is likely that Railway just needs to rebuild with the new code.

---

## Next Steps

1. **Immediate**: Trigger a manual deployment in Railway dashboard
2. **Then**: Monitor build logs for errors
3. **Finally**: Test the health endpoint once build completes

If you have access to the Railway dashboard, the **New Deployment** button is the fastest way to get the latest code running.

---

**Need Help?**
- Railway docs: https://docs.railway.app/
- GitHub repo: https://github.com/nebellleben/capstone-polymarket-arbitrage-agent
- Latest fixes: commits 43ab342, 747d999, b9df8e5, b688094, 6f43607
