# Railway Deployment Instructions

## Latest Updates (2026-01-14)

### Bug Fixes Applied:
1. ✅ Fixed `@property` decorator bug in `opportunity.py` - `is_profitable()` method
2. ✅ Added market price filter to exclude zero-price markets
3. ✅ Fixed database path configuration (now uses `./data` instead of `/app/data`)
4. ✅ Fixed severity Enum/string handling in alert generation
5. ✅ Updated Dockerfile timestamp for cache invalidation

### System Status:
- **Local**: Detection worker running successfully (PID 60708)
- **Previous Results**: 12 opportunities detected with 4-24% profit margins
- **APIs**: Brave Search (30 articles), Polymarket (99 markets, 19 with prices)

---

## Quick Deploy Steps

### Option 1: Interactive Login (Recommended)

```bash
# 1. Login to Railway (opens browser)
railway login

# 2. Verify you're connected
railway status

# 3. Deploy latest code
railway up

# 4. Monitor deployment
railway logs

# 5. Check environment variables
railway variables
```

### Option 2: Using Railway Token

If you have a Railway token:

```bash
# 1. Set token (get from: https://railway.app/account/tokens)
export RAILWAY_TOKEN="your_token_here"

# 2. Deploy
railway up

# 3. Monitor logs
railway logs
```

---

## What Gets Deployed

### Files Included:
- ✅ All bug fixes in `src/models/opportunity.py`
- ✅ Price filter in `src/workflows/mvp_workflow.py`
- ✅ Database config in `src/utils/config.py` and `src/database/connection.py`
- ✅ Alert generation fixes in `src/agents/alert_generator.py`
- ✅ Updated `Dockerfile` with new timestamp
- ✅ `requirements.txt` with `google-generativeai` package

### Environment Variables Needed:
Railway should already have these configured:
- `BRAVE_API_KEY` - Brave Search API key
- `GEMINI_API_KEY` - Google Gemini API key
- `GEMINI_MODEL` - Model name (gemini-2.5-flash)
- `TELEGRAM_BOT_TOKEN` - Telegram bot token
- `TELEGRAM_CHAT_ID` - Your chat ID
- `TELEGRAM_ENABLED` - Set to "true"
- `LOG_LEVEL` - INFO
- `CONFIDENCE_THRESHOLD` - 0.2
- `MIN_PROFIT_MARGIN` - 0.02
- `NEWS_SEARCH_INTERVAL` - Detection cycle interval in seconds (default: 600 = 10 minutes)

---

## Verification Steps

After deployment:

```bash
# 1. Check service status
railway status

# 2. View logs (should see "system_start", "telegram_notifications_enabled")
railway logs -f

# 3. Monitor for opportunities (look for "opportunity_detected" events)
railway logs | grep opportunity_detected

# 4. Check health endpoint
curl https://your-service-url.railway.app/api/health
```

---

## Troubleshooting

### Issue: "Unauthorized" Error
**Solution**: Run `railway login` in your terminal (not through Claude)

### Issue: Service Not Starting
**Check**: Logs for errors
```bash
railway logs -f
```

### Issue: No Alerts Generated
**Expected**: First cycle takes 5-6 minutes (reasoning phase)
**Wait**: 6 minutes before checking for alerts

### Issue: Database Path Error
**Fixed**: Database now uses `/app/data` in production, `./data` locally

---

## Expected Output

When running correctly, you should see logs like:

```json
{"event": "system_start", ...}
{"event": "telegram_notifications_enabled", ...}
{"event": "cycle_begin", "number": 1, ...}
{"event": "brave_search_success", "results": 30, ...}
{"event": "markets_fetched", "count": 99, "active": true, ...}
{"event": "opportunities_detected", "opportunities_found": 12, ...}
{"event": "alert_created", "alert_id": "alert-...", ...}
{"event": "telegram_sent", "message_id": ..., ...}
```

---

## Next Steps

1. **Login to Railway** (required for deployment)
2. **Run `railway up`** to deploy
3. **Monitor logs** with `railway logs -f`
4. **Verify alerts** are sent to Telegram

---

## Need Help?

- Railway Dashboard: https://railway.app/
- Railway Docs: https://docs.railway.app/
- Project Repo: https://github.com/your-repo
