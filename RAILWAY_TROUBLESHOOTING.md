# Railway Deployment Troubleshooting

## Issue 1: API Key Not Set 🔑

**Symptom**: Logs show `brave_api_key not set, returning mock data`

**Root Cause**: Environment variable not properly configured in Railway

### Solution: Correctly Set Environment Variables in Railway

1. **Go to your Railway project**
2. **Click on your service** (the app service, not database)
3. **Click "Variables" tab** in left sidebar
4. **Add the variable** (EXACTLY as shown):

| Name | Value |
|------|-------|
| `BRAVE_API_KEY` | `BSA_qx3AXzyRx8q19qZE9ZrxVULcaRP` |

**Important**:
- Name must be **ALL UPPERCASE**: `BRAVE_API_KEY`
- Value must be **exact** (no spaces): `BSA_qx3AXzyRx8q19qZE9ZrxVULcaRP`
- Click **"Create"** or **"Save"**

5. **Redeploy**:
   - Click **"New Deploy"** (top right)
   - Click **"Redeploy"**
   - Wait for build to complete (1-2 minutes)

6. **Verify**:
   - Go to **"Logging"** tab
   - Look for: `✓ API configured: BRAVE_API_KEY present`
   - You should NO LONGER see: `brave_api_key not set`

---

## Issue 2: Logging Errors 🐛

**Symptom**: Logs show `Logger._log() got an unexpected keyword argument 'query'`

**Status**: ✅ **FIXED** (as of commit `88ce130`)

### Solution: Redeploy to Get the Fix

1. **Click "New Deploy"** button (top right)
2. **Click "Redeploy"**
3. Wait for build to complete

The new code includes centralized logging configuration that properly handles keyword arguments.

---

## Issue 3: Container Keeps Restarting 🔄

**Symptom**: Logs show "Starting Container" repeatedly

**Possible Causes**:

### Cause A: Application Crashing
1. Check **"Logging"** tab for Python errors
2. Look for exceptions or tracebacks
3. Common issues:
   - Missing dependencies
   - Import errors
   - Configuration errors

### Cause B: Memory Limits
1. Go to **"Settings"** tab
2. Check **"RAM"** allocation
3. Increase if needed (recommended: 512MB - 1GB)

---

## How to Verify Your Deployment is Working ✅

After fixing both issues and redeploying, you should see:

```
✓ Starting arbitrage detection system
✓ API configured: BRAVE_API_KEY present
✓ Fetched 10 news articles from Brave Search
✓ Fetched 100 active Polymarket markets
✓ Analyzing market impacts...
🎯 Detected 2 arbitrage opportunities
🚨 Generated 2 alerts
```

**Key Indicators**:
- ✅ No "brave_api_key not set" messages
- ✅ No "Logger._log()" errors
- ✅ Real news articles fetched (not mock data)
- ✅ Opportunities detected (> 0)

---

## Debug Mode: Enable Verbose Logging

If you still have issues, enable debug logging:

1. In Railway **"Variables"** tab, add:
   ```
   LOG_LEVEL=DEBUG
   ```

2. Redeploy

3. Check logs for detailed information about:
   - Environment variables loaded
   - API calls made
   - Data processed
   - Errors encountered

---

## Common Railway Questions

### Q: Where is my app's URL?
**A**:
- Click on your service
- Look at the top of the page
- You'll see a URL like: `https://your-app.up.railway.app`

**Note**: This is a background worker, not a web app, so the URL won't show a webpage. Use the "Logging" tab instead to monitor activity.

### Q: Why does the container stop and start?
**A**:
- The workflow runs one cycle, then exits
- Railway automatically restarts it
- This is normal behavior for a worker process

### Q: How much will this cost?
**A**:
- Free tier: $5 credit (first month)
- After that: ~$5-10/month
- You can set a budget in Railway settings

### Q: How do I stop the service?
**A**:
- Go to your service
- Click **"Settings"** tab
- Click **"Delete Service"** (bottom)
- Or click the pause button to temporarily stop

---

## Still Having Issues?

### Check These Things:

1. **Environment Variables**:
   - Go to **Variables** tab
   - Verify `BRAVE_API_KEY` is set correctly
   - Make sure there are no typos

2. **Build Status**:
   - Check if build is green (completed)
   - If red (failed), check build logs

3. **Service Status**:
   - Should show 🟢 green circle
   - If 🔴 red, check logs for errors

4. **Redeploy**:
   - Sometimes a fresh redeploy fixes issues
   - Click **"New Deploy"** → **"Redeploy"**

---

## Quick Checklist

Before deploying, verify:

- [ ] `BRAVE_API_KEY` is set in Railway Variables
- [ ] Value is: `BSA_qx3AXzyRx8q19qZE9ZrxVULcaRP`
- [ ] Name is ALL UPPERCASE (no typos)
- [ ] You've clicked "Redeploy" after setting variables
- [ ] Build completed successfully (green)
- [ ] Logs show "API configured: BRAVE_API_KEY present"
- [ ] No "Logger._log()" errors
- [ ] Opportunities are being detected

---

## Expected System Behavior

When working correctly, your system will:

1. **Every 60 seconds**:
   - Fetch breaking news from Brave Search
   - Fetch active Polymarket markets
   - Analyze which news affects which markets
   - Detect price discrepancies
   - Generate alerts when profitable opportunities found

2. **Track metrics**:
   - Opportunities detected per cycle
   - Alerts generated
   - API usage
   - Performance metrics

3. **Continue running**:
   - Railway auto-restarts if it crashes
   - Runs continuously in the cloud
   - No manual intervention needed

---

**Last Updated**: 2025-01-12
**For issues**: Check logs first, then try redeploying
