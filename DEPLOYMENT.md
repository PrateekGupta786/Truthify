# Truthify Deployment Guide

## ⚡ FREE DEPLOYMENT - NO CREDIT CARD NEEDED!

**Don't want to pay for Render?** Use **Hugging Face Spaces** instead!

### 🏆 Recommended: Hugging Face Spaces (FREE)
- ✅ No credit card
- ✅ Designed for ML models
- ✅ Plenty of disk/memory
- ✅ Model loads perfectly
- ✅ Easy 5-minute setup

👉 **[See FREE_DEPLOYMENT.md for full instructions](FREE_DEPLOYMENT.md)**

---

## 🔴 CRITICAL ISSUE: Model Not Loading (45% Confidence)

**Problem**: Your app always shows "Real Image" with 45% confidence on Render/Netlify.

**Root Cause**: 
- The AI model (~500MB) fails to download during app startup
- Free tier Render has only 500MB disk → model download times out
- App falls back to heuristic mode (metadata/hash matching only)

**Solution**: Use **Standard** (paid) tier on Render, or use the new build configuration below.

---

## ✅ Fixed Configuration Files

These files have been updated to fix the issue:

### 1. **requirements.txt**
- Changed to CPU-only PyTorch (smaller: 150MB vs 2GB)

### 2. **start.sh** (NEW)
- Downloads model during BUILD time (not startup)
- Sets 10-minute timeout for large files
- Better error logging

### 3. **render.yaml** (NEW)
- Configures Render build process correctly
- Pre-downloads model to cache
- Sets environment variables

### 4. **main.py** (UPDATED)
- Added timeout handling
- Better error messages
- Environment variable configuration

---

## 🚀 Deploy to Render (Backend)

### Step 1: Prepare GitHub
```bash
git add .
git commit -m "Fix model loading for deployment"
git push
```

### Step 2: Create Render Service
1. Go to https://render.com
2. Dashboard → **New** → **Web Service**
3. Connect your GitHub repo
4. Configuration:
   ```
   Name: truthify
   Region: Oregon (US)
   Runtime: Python 3.11
   Build command: (leave blank - render.yaml handles it)
   Start command: uvicorn main:app --host 0.0.0.0 --port 8000
   ```

5. **Important**: Select **Standard** plan (NOT Free)
   - Free tier: 500MB disk (NOT enough for model)
   - Standard tier: 2GB+ disk (sufficient)

6. Environment Variables (add these):
   ```
   HF_HUB_TIMEOUT = 600
   TRANSFORMERS_CACHE = .cache/huggingface
   PYTHONUNBUFFERED = 1
   ```

7. Click **Create Web Service**

### Step 3: Wait for Build
- Build takes 5-10 minutes
- Watch logs for: `✓ Model ready on cpu`
- If you see `✗ Model load failed` → check storage/memory

### Step 4: Get Backend URL
- Once deployed, you'll see: `https://truthify-xxxxx.onrender.com`
- Test it: `https://truthify-xxxxx.onrender.com/api/health`

---

## 📱 Deploy to Netlify (Frontend Only)

### Step 1: Update Frontend
Edit `static/index.html` and find the API URL configuration:

```javascript
// Change this:
const API_URL = "http://localhost:8000/api";

// To your Render backend:
const API_URL = "https://truthify-xxxxx.onrender.com/api";
```

### Step 2: Deploy
1. Go to https://netlify.com
2. New Site → Import from Git
3. Select your repo
4. Build command: (leave blank)
5. Publish directory: `static`
6. Deploy

---

## 🔍 Verify Everything Works

### Check Backend Model:
```bash
curl https://truthify-xxxxx.onrender.com/api/health
```

**Expected**:
```json
{
  "status": "ok",
  "model_ready": true,
  "model_error": null,
  "model_id": "Ateeqq/ai-vs-human-image-detector"
}
```

### Check Frontend:
- Visit your Netlify URL
- Login with: admin / password
- Upload an image
- Should see AI detection score (not 45%)

---

## ⚠️ Troubleshooting

### Model still shows 45% confidence
1. Check Render logs: `https://dashboard.render.com/`
2. Look for `✓ Model ready` or `✗ Model load failed`
3. If failed, you need **Standard** tier (minimum)

### Build times out
- Render free tier: max 30 min build
- Switch to Standard plan for longer builds

### Disk space error
- Free tier: 500MB (too small)
- Standard tier: 2GB (sufficient for ~1.5GB model+deps)

### Network timeout  
- Hugging Face CDN may be slow
- Set `HF_HUB_TIMEOUT = 900` (15 minutes)

---

## 📊 Model Status

| Tier | Result |
|------|--------|
| Local | ✅ Model loads fine |
| Netlify | ❌ Backend not supported (frontend only) |
| Render Free | ❌ Disk too small (45% fallback mode) |
| Render Standard | ✅ Works perfectly |
| Railway/Fly.io | ✅ Works with enough disk |

---

## 🛠️ Local Development

```bash
# Install
pip install -r requirements.txt

# Run
python run.py

# Test
curl http://localhost:8000/api/health

# Open dashboard
http://localhost:8000
Login: admin / password
```

---

**Updated**: July 2026 - Fixed deployment model loading issues

```

## Deploy Frontend To Netlify

1. Create a new Netlify site from the same GitHub repo.
2. Netlify will use `netlify.toml`.
3. Publish directory should be:

```text
static
```

4. Open the Netlify site.
5. Go to Settings.
6. Paste your deployed backend URL into `Backend API URL`.
7. Click Save Changes.
8. Login with `admin` / `password`.

## Reviewer Flow

1. Open the Netlify website.
2. Login using `admin` / `password`.
3. Upload an image.
4. The selected image preview appears below the upload box.
5. Truthify checks model probability, C2PA-like markers, EXIF/XMP generator tags, and the local perceptual-hash database.
