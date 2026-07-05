# Truthify - AI Content Protection Platform

A hybrid AI detection system that combines vision transformers, C2PA provenance checking, EXIF/XMP metadata analysis, and perceptual hashing to identify synthetic and AI-generated images.

## 🎯 Features

- **Multi-Signal Detection**: Model probability + C2PA manifest + EXIF/XMP keywords + pHash similarity
- **Real-time Analysis**: Upload images or provide URLs for instant analysis
- **Evidence Pipeline**: Visual breakdown of detection signals
- **Reference Database**: Build a local library of known AI-generated samples
- **Dark Mode**: Built-in theme toggle with persistence
- **Responsive Design**: Works on desktop and mobile

## 🚀 Quick Start (Local Development)

### Prerequisites
- Python 3.11+
- pip

### Setup
```bash
pip install -r requirements.txt
python run.py
```

Open `http://127.0.0.1:8000` and login with:
- **Username**: admin
- **Password**: password

## 📦 Deployment

### Backend Deployment (Render)

1. **Create Render Account**: https://render.com (free tier)
2. **Connect GitHub**: Link your GitHub account in Render settings
3. **Create Web Service**:
   - Name: `truthify-api`
   - Runtime: Python 3.11
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - Free tier is sufficient
4. **Copy Backend URL** after deployment (looks like `https://truthify-api.onrender.com`)

### Frontend Deployment (Netlify)

1. **Create Netlify Account**: https://netlify.com (free)
2. **Connect GitHub**: Authorize Netlify to access your repos
3. **Create Site**:
   - Select your GitHub repo
   - Publish directory: `static`
   - Build command: (leave empty)
   - Click Deploy
4. **Connect Backend**:
   - Go to Site Settings → Environment
   - Add variable: `REACT_APP_API_URL` = your Render backend URL
   - Or manually update in dashboard settings after login

## ⚙️ Configuration

### Environment Variables (Optional)

Create a `.env` file in the root:
```
LOGIN_USERNAME=admin
LOGIN_PASSWORD=password
```

### Updating Backend URL in Frontend

After deploying the backend:
1. Visit your Netlify site
2. Login with admin/password
3. Go to Settings
4. Paste your Render backend URL
5. Click Save

The app will remember this for all future uses.

## 📊 How It Works

### Detection Pipeline

1. **Image Upload/URL**: User provides image via upload or URL
2. **Metadata Extraction**: EXIF/XMP tags scanned for generator hints
3. **Perceptual Hash**: Compute dhash and compare against reference database
4. **Vision Transformer**: Run Ateeqq model for AI/real classification
5. **C2PA Check**: Inspect for content credentials markers
6. **Score Aggregation**: Combine all signals into final confidence score
7. **Verdict**: Display prediction, confidence, and evidence chain

### Detection Signals

| Signal | Purpose | Confidence Boost |
|--------|---------|------------------|
| Model Probability | Vision Transformer output | 0-100% |
| C2PA Manifest | Content credentials found | +97% if AI signature |
| XMP Keywords | Generator tool metadata | +95% if found |
| pHash Match | Known AI sample database | Up to +92% |
| No EXIF | Stripped metadata | +55% if missing |

## 🔐 Authentication

Default credentials (change in production):
- **Username**: admin
- **Password**: password

Each login generates a unique bearer token stored in localStorage.

## 📁 Project Structure

```
truthify/
├── main.py              # FastAPI backend
├── run.py               # Local dev server
├── requirements.txt     # Python dependencies
├── runtime.txt          # Python version spec
├── netlify.toml         # Netlify config
├── reference_hashes.json # pHash reference DB
├── static/
│   └── index.html       # Frontend (Tailwind + Vanilla JS)
└── data/
    └── reference_hashes.json (auto-created)
```

## 📡 API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/login` | POST | Authenticate user |
| `/api/me` | GET | Get current user info |
| `/api/analyze/file` | POST | Analyze uploaded image |
| `/api/analyze/url` | POST | Analyze image from URL |
| `/api/stats` | GET | Get scan statistics |
| `/api/history` | GET | Get past scan results |
| `/api/library` | GET | Get reference samples |
| `/api/library/add` | POST | Save fingerprint to DB |
| `/api/notifications` | GET | Get alerts |
| `/api/health` | GET | Backend status |

## 🎓 Model Information

- **Model**: Ateeqq/ai-vs-human-image-detector (HuggingFace)
- **Architecture**: SigLIP (Vision Transformer)
- **Task**: Binary classification (AI Generated vs Real Image)
- **Auto-download**: ~2GB on first run (cached after)

## ⚡ Performance

- **Inference Time**: 200-500ms per image (depends on GPU availability)
- **Supported Formats**: JPEG, PNG, WebP
- **Max File Size**: ~10MB (Render limit)

## 🐛 Troubleshooting

### Backend fails to start
```
Check logs: Render Dashboard → Logs
Common issues:
- Model download timeout (increase timeout in Render)
- Memory limit exceeded (upgrade to Starter plan if needed)
- Missing requirements.txt
```

### Frontend won't connect to backend
- Verify backend URL in Settings
- Check CORS: backend must allow your Netlify domain
- Check browser console for errors (F12 → Console)

### Model takes too long to load
- First request loads model (~30s)
- Subsequent requests are faster
- Consider Render Starter plan for persistent memory


## 📧 Support

For issues or questions during review, check:
1. Render logs (backend status)
2. Browser console (frontend errors)
3. Network tab (API call failures)
