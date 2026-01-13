# Railway 502 Error - EXPOSE Directive Applied But Still Failing

## Current Status

✅ **Applied Fixes**:
- Added `EXPOSE 8080` to Dockerfile (line 73)
- Removed `PORT = "8080"` from railway.toml
- Local testing: PASS (http://localhost:8080/api/health returns 200)

❌ **Railway Deployment**: Still returns HTTP 502

## Deployment Log Analysis

From `/Users/kelvinchan/Downloads/logs.1768266095229.log`:

### ✅ What's Working Inside Container
```
Line 3: Railway PORT: 8080
Line 29: INFO: Uvicorn running on http://0.0.0.0:8080
Line 28: Application startup complete
Line 39: ✓ Services started successfully
Line 40: Worker PID: 4
Line 41: Web Server PID: 5
```

### ❌ What's Failing
- External access returns HTTP 502
- Railway's Edge Proxy cannot reach the container

## Root Cause

The application is running correctly inside the container, but **Railway's service configuration has a port mismatch**.

Even with the `EXPOSE 8080` directive, Railway needs to be configured to route traffic to port 8080 in the service settings.

## 🔧 Solution: Configure Railway Service Port

### Step 1: Access Railway Service Settings

1. Go to https://railway.app/
2. Open project: `capstone-polymarket-arbitrage-agent`
3. Click on the service (the main app service)
4. Click on the **Settings** tab

### Step 2: Find Port Configuration

Look for one of these fields (location varies by Railway version):
- **"Port"** field
- **"Listening Port"** field
- **"Container Port"** field
- **"Target Port"** field (in Domains/Networking section)

### Step 3: Set Port to 8080

Enter `8080` in the port field and save.

### Step 4: Trigger Redeployment

After saving the port setting:
1. Click **"New Deployment"** or **"Redeploy"**
2. Wait 2-3 minutes for build

### Step 5: Verify

Test the endpoint:
```bash
curl https://capstone-polymarket-arbitrage-agent-production.up.railway.app/api/health
```

Expected: HTTP 200 with `{"status":"healthy",...}`

---

## 🖼️ Visual Guide: Where to Find Port Setting

### Option A: Service Settings → Port
```
Railway Dashboard
  └─ capstone-polymarket-arbitrage-agent
      └─ [Your Service Name]
          └─ Settings tab
              └─ Port field → Enter "8080"
```

### Option B: Service Settings → Networking
```
Railway Dashboard
  └─ capstone-polymarket-arbitrage-agent
      └─ [Your Service Name]
          └─ Settings tab
              └─ Networking section
                  └─ Port → Enter "8080"
```

### Option C: Domains Settings
```
Railway Dashboard
  └─ capstone-polymarket-arbitrage-agent
      └─ [Your Service Name]
          └─ Settings tab
              └─ Domains section
                  └─ [Click on domain]
                      └─ Target Port → Enter "8080"
```

---

## 🔍 Verification Steps

### 1. Check Current Railway Configuration

In Railway dashboard, verify:
- Service type: **Dockerfile** (not "Nixpacks" or other)
- Dockerfile path: **Dockerfile** (or `/Dockerfile`)
- Root directory: **`.`** (empty or current directory)
- Port: **8080** (critical!)

### 2. Verify Docker Build

Check that Railway built the Dockerfile with EXPOSE:
1. Go to **Deployments** tab
2. Click on latest deployment
3. View **Build Logs**
4. Should see: "Sending build context to Docker daemon"
5. Should NOT see errors about Dockerfile

### 3. Verify Container Logs

Container logs should show:
```
Railway PORT: 8080
Web Server Port: 8080
INFO: Uvicorn running on http://0.0.0.0:8080 (Press CTRL+C to quit)
```

If you see these, the container is running correctly.

---

## 🚨 Alternative: Railway May Need Explicit Port Declaration

Some Railway deployments require explicitly declaring the port in the Dockerfile CMD or in railway.toml.

### Option 1: Add PORT to docker-entrypoint.sh explicitly

If the port setting in Railway dashboard doesn't work, we may need to ensure the PORT is explicitly set in the startup script.

### Option 2: Check if Railway is using different service type

Verify Railway isn't trying to auto-detect the service type:
1. In service Settings
2. Check **"Service Type"** or **"Build Type"**
3. Should be **"Dockerfile"** (not "Nixpacks" or "Auto")

---

## 📋 Diagnostic Checklist

Before assuming it's a port issue:

- [ ] Dockerfile has `EXPOSE 8080` directive ✓ (done)
- [ ] railway.toml does NOT set PORT variable ✓ (done)
- [ ] Railway service type is "Dockerfile"
- [ ] Railway service Port field is set to "8080"
- [ ] Railway root directory is "." or empty
- [ ] Dockerfile path is "Dockerfile" or "/Dockerfile"
- [ ] Latest deployment shows "Running" status
- [ ] Container logs show "Uvicorn running on http://0.0.0.0:8080"

---

## 💡 Why This Happens

Railway has multiple ways to configure a service:
1. **Dockerfile**: Builds from Dockerfile, reads EXPOSE directive
2. **Nixpacks**: Auto-detects language, builds automatically
3. **Manual**: Uses start command

When using Dockerfile:
- Railway reads EXPOSE directive
- But ALSO needs Port field in service settings
- The Port field tells Railway's proxy where to forward traffic
- Without this field, Railway doesn't know which external port maps to container port 8080

---

## 🎯 Expected Outcome

After setting the Port field to 8080 in Railway settings:

1. Railway rebuilds the deployment
2. Railway's Edge Proxy knows to forward traffic to container port 8080
3. External requests reach the application
4. Health check returns HTTP 200
5. Dashboard loads successfully

---

## 📞 If Still Failing After Port Configuration

If setting the Port to 8080 doesn't fix it:

1. **Check Railway Service Type**:
   - Ensure it's set to "Dockerfile"
   - Not "Nixpacks" or "Auto"

2. **Verify Railway Environment Variables**:
   - In Settings → Variables
   - PORT should be blank (let Railway auto-inject)
   - ENVIRONMENT should be "production"

3. **Try Adding Explicit Port Mapping**:
   - Some Railway deployments need: `PORT=8080` in Variables
   - Try adding it back if removing it didn't help

4. **Check for Multiple Services**:
   - Ensure you're deploying to the correct service
   - Railway might have multiple services (worker, web, etc.)
   - Port configuration needs to be on the web/API service

5. **Contact Railway Support**:
   - https://support.railway.app
   - Provide deployment logs and Dockerfile
   - They can check service configuration on their end

---

**Most Likely Fix**: Set **Port = 8080** in Railway service Settings tab, then redeploy.
