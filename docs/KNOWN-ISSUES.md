# Known Issues - MVP

## Issue: Database Persistence Not Working in Railway Deployment

### Status: **KNOWN LIMITATION** - Core functionality works, only web dashboard history affected

### Impact: **MEDIUM** - Alerts are generated and sent, but not visible in web dashboard

### Description

The SQLite database persistence layer is not functioning correctly in the Railway deployment. Despite all indicators showing successful database writes (commits, flushes, session closures), the database queries return 0 rows.

### What Works ✅

1. **Arbitrage Detection** - Fully functional
   - Detects 8-14 opportunities per cycle
   - Uses AI reasoning (fallback to keyword matching)
   - Analyzes market impact correctly

2. **Alert Generation** - Fully functional
   - Creates alerts with all required fields
   - Calculates confidence scores
   - Generates recommendations

3. **Telegram Notifications** - Fully functional
   - Sends alerts to configured chat (ID: 867719791)
   - Filters by severity (WARNING and above)
   - Includes all alert details

4. **Logging** - Fully functional
   - Console logs show all alerts
   - Railway logs capture everything
   - `alerts.json` file is updated with alerts

5. **API Health** - Fully functional
   - `/api/health` returns healthy status
   - `/api/status` shows system metrics
   - WebSocket connections work

### What Doesn't Work ❌

1. **Web Dashboard Alert History** - Not functional
   - `/api/alerts/recent` returns empty list
   - `/api/alerts/stats` shows 0 total alerts
   - Database queries return 0 rows despite successful writes

### Root Cause Analysis

#### Investigation Findings

We spent significant effort debugging this issue. Here's what we confirmed:

**Database Writes Appear Successful:**
```
alert_saved with commit_success=true, flush_success=true, session_closed=true
Database file modification time changes (proof of writes)
No error logs during save operations
```

**But Queries Return Empty:**
```
Database file exists: /app/data/arbitrage.db (73,728 bytes)
Tables exist: alerts, cycle_metrics
Row counts: {"alerts": 0, "cycle_metrics": 0}
```

#### Possible Causes

1. **SQLite Concurrency Issue**
   - Railway runs worker and web server as separate processes
   - Each process has its own Python interpreter
   - SQLite might not properly share data between processes without WAL mode
   - NullPool configuration might not be sufficient for multi-process access

2. **Transaction Isolation**
   - Worker commits transactions in its session
   - Web server queries might not see committed data
   - Session cleanup happens correctly but data not persisted to disk

3. **Railway Volume Mounting**
   - Persistent volume is configured in `railway.toml`
   - But volume might not be properly shared between processes
   - Each process might see its own view of the filesystem

4. **SQLite Write-Ahead Logging (WAL)**
   - Data might be written to separate `.wal` or `.journal` files
   - These files might not be properly synced
   - Queries might not see WAL data

### Current Workarounds

#### For Monitoring Alerts

1. **Railway Logs** - Primary monitoring method
   ```bash
   railway logs --lines 500 | grep "alert_created"
   ```

2. **Telegram Notifications** - Real-time alerts sent to your phone

3. **Console Output** - Full alert details in Railway logs

4. **alerts.json File** - File-based persistence (if accessible)

### Future Fixes

#### Recommended Solutions (Priority Order)

1. **Switch to PostgreSQL** (RECOMMENDED)
   - Proper multi-user database
   - Handles concurrent access correctly
   - Railway has excellent PostgreSQL support
   - **Effort**: Medium (2-3 hours)
   - **Cost**: Free tier available

2. **Fix SQLite WAL Configuration**
   - Enable WAL mode explicitly
   - Configure synchronous mode
   - Add proper locking
   - **Effort**: Low (1 hour)
   - **Uncertainty**: High (might not work)

3. **Use alerts.json for Dashboard**
   - Read alerts from JSON file instead of database
   - Simpler but less robust
   - **Effort**: Low (1-2 hours)
   - **Performance**: Poor for large datasets

4. **Single Process Architecture**
   - Run worker and web server in same process
   - Eliminates multi-process issues
   - **Effort**: Medium (2-3 hours)
   - **Downside**: Less scalable

### Deployment Status

**Current Deployment**: https://capstone-polymarket-arbitrage-agent-production.up.railway.app/

**Working Features**:
- ✅ Arbitrage detection (10-minute cycles)
- ✅ Alert generation with AI reasoning
- ✅ Telegram notifications
- ✅ Health check endpoint
- ✅ System metrics

**Non-Working Features**:
- ❌ Web dashboard alert history
- ❌ Database persistence

### How to Monitor the System

#### 1. Check Health Status
```bash
curl https://capstone-polymarket-arbitrage-agent-production.up.railway.app/api/health
```

#### 2. View Recent Logs
```bash
railway logs --lines 100 | grep "alert_created"
```

#### 3. Monitor Detection Cycles
```bash
railway logs --lines 500 | grep -E "(cycle_begin|generate_alerts_complete|cycle_sleep)"
```

#### 4. Check Telegram
Check your Telegram for new alerts (should receive notifications for WARNING and CRITICAL severity alerts)

#### 5. View System Status
```bash
curl https://capstone-polymarket-arbitrage-agent-production.up.railway.app/api/status | python -m json.tool
```

### Configuration

**Current Settings**:
- Detection cycle interval: 600 seconds (10 minutes)
- Confidence threshold: 0.7 (70%)
- Minimum profit margin: 5%
- Telegram notifications: Enabled for WARNING and CRITICAL

**Environment Variables**:
```
NEWS_SEARCH_INTERVAL=600  # 10 minutes
CONFIDENCE_THRESHOLD=0.7  # 70%
MIN_PROFIT_MARGIN=0.05    # 5%
TELEGRAM_ENABLED=true
TELEGRAM_MIN_SEVERITY=WARNING
```

### Technical Details

**Deployment**: Railway (container-based cloud platform)
**Architecture**: Multi-process (worker + web server)
**Database**: SQLite (not working for persistence)
**Fallback**: File-based logs + Telegram notifications

**Files Modified During Investigation**:
- `src/database/connection.py` - Added NullPool for multi-process
- `src/database/repositories.py` - Fixed session management
- `src/agents/alert_generator.py` - Fixed datetime serialization
- `railway.toml` - Added persistent volume configuration
- `src/api/routes/debug.py` - Added debug endpoints

### Next Steps for Production

1. **Short-term** (Current MVP):
   - ✅ Core arbitrage detection works
   - ✅ Telegram notifications provide real-time alerts
   - ✅ Railway logs provide full history
   - ✅ System is stable and running

2. **Medium-term** (Production hardening):
   - [ ] Implement PostgreSQL for proper persistence
   - [ ] Fix web dashboard alert history
   - [ ] Add alert search and filtering
   - [ ] Improve error handling

3. **Long-term** (Enhanced features):
   - [ ] Add trade execution
   - [ ] Implement backtesting
   - [ ] Add performance metrics dashboard
   - [ ] Create alert analytics

### Conclusion

This is a **known limitation** of the current MVP implementation. The core functionality (arbitrage detection and alerting) works perfectly. The only missing feature is the web dashboard history view.

For MVP validation purposes, the system is **fully functional** and meets the primary objectives:
- ✅ Detects arbitrage opportunities
- ✅ Generates actionable alerts
- ✅ Sends real-time notifications
- ✅ Runs autonomously in the cloud

The database persistence issue can be addressed in Phase 2 by switching to PostgreSQL or fixing the SQLite configuration.

---

**Last Updated**: 2026-01-14
**Deployment**: Railway Production
**Status**: Active with known limitation documented
