# Railway Deployment Guide

## Quick Start (5 minutes)

### Step 1: Create Railway Account
1. Go to https://railway.app/
2. Click "Login" and sign up with GitHub (recommended)

### Step 2: Create New Project
1. Click **"New Project"** button
2. Select **"Deploy from GitHub repo"**
3. Find and select: `nebellleben/capstone-polymarket-arbitrage-agent`
4. Click **"Add to Project"**

### Step 3: Configure Environment Variables
1. Click on your new project (it will say "New Project" or the repo name)
2. Click the **"Variables"** tab
3. Add these variables:

| Name | Value |
|------|-------|
| `BRAVE_API_KEY` | `BSA_qx3AXzyRx8q19qZE9ZrxVULcaRP` |
| `LOG_LEVEL` | `INFO` |
| `ENVIRONMENT` | `production` |

4. Click **"Create Variables"** or **"Save"**

### Step 4: Deploy
1. Click **"Deploy Now"** or **"Trigger Deploy"**
2. Wait for the build to complete (2-3 minutes)
3. You'll see a green checkmark when done ✅

### Step 5: Monitor Your App
1. Click on the **app-xxxx** service
2. Click the **"Logging"** tab to see real-time logs
3. You should see output like:
   ```
   ✓ Starting arbitrage detection system
   ✓ API configured: BRAVE_API_KEY present
   📰 Fetching news...
   🔍 Analyzing impacts...
   ```

### Step 6: Get Your App URL
1. Click the **"Networking"** tab (or scroll to top)
2. Copy your **Public URL** (e.g., `https://your-app.up.railway.app`)

---

## What Your System Does

Once deployed, your system will:

✅ **Every 60 seconds**:
- Fetch breaking news via Brave Search API
- Analyze market impact using AI reasoning
- Fetch Polymarket prices
- Detect arbitrage opportunities
- Generate alerts when profitable discrepancies found

✅ **Track metrics**:
- Opportunities detected per cycle
- API usage and latencies
- Alert generation rates

---

## View Metrics

After running for a while, you can analyze performance:

```bash
# SSH into your Railway container (optional)
railway open

# Inside the container, run:
python scripts/analyze-metrics.py
```

---

## Troubleshooting

### Build Fails
- Check the **"Build Logs"** tab
- Make sure `BRAVE_API_KEY` is set correctly
- Try redeploying: click **"New Deploy"** → **"Redeploy"**

### No Logs Appearing
- Click the **"Logging"** tab
- Make sure you're looking at the **app-xxxx** service (not Postgres if it created one)
- Wait 1-2 minutes after deployment for first logs

### Service Not Responding
- Check **"Metrics"** tab for CPU/Memory usage
- Click **"Redeploy"** to restart
- Check if environment variables are set correctly

---

## Cost

**Free tier**: Up to $5/month credit
- After free credit: ~$5-10/month for this workload
- To control costs: Set a budget in Railway settings

---

## Next Steps

1. ✅ Deploy to Railway
2. ✅ Monitor logs for opportunities
3. ✅ Add `ANTHROPIC_API_KEY` for better AI reasoning (optional)
4. ✅ Adjust thresholds if needed (`CONFIDENCE_THRESHOLD`, `MIN_PROFIT_MARGIN`)
5. ✅ Analyze metrics weekly

---

## Example Output

When working correctly, you'll see logs like:

```
[2025-01-12 10:00:00] Starting detection cycle cycle-001
[2025-01-12 10:00:02] ✓ Fetched 10 news articles
[2025-01-12 10:00:05] ✓ Fetched 25 active markets
[2025-01-12 10:00:10] ✓ Analyzed 5 significant impacts
[2025-01-12 10:00:12] 🎯 Detected 2 arbitrage opportunities
[2025-01-12 10:00:13] 🚨 Generated 2 alerts

ALERT: Trump approval odds at 0.35 should be 0.50 (43% profit)
  News: Breaking: New polling data shows...
  Confidence: 85%

[2025-01-12 10:01:00] Starting detection cycle cycle-002
```

---

**Need Help?** Check Railway docs: https://docs.railway.app/
