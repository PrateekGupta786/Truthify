# 🛡️ Truthify — AI Content Protection Platform

> **Edunet Foundation Capstone Internship Project**  
> Detect AI-generated & synthetic images using a multi-signal ensemble of deep learning, metadata analysis, and perceptual hashing.

---

## 📌 Problem Statement

The rapid rise of generative AI tools (Midjourney, DALL-E, Stable Diffusion, FLUX) has made it trivially easy to create hyper-realistic synthetic images. These are increasingly being used in:
- **Disinformation campaigns** and fake news
- **Identity fraud** and deepfake scams
- **Copyright abuse** and content manipulation

Traditional single-model classifiers have high false-positive rates and are easily fooled. There was a need for a **multi-signal, evidence-based detection system** that combines multiple independent signals to reach a confident verdict.

---

## 💡 Proposed Solution — Truthify

Truthify is a hybrid AI media authenticity platform that combines **four independent detection signals** into a single confidence score:

| Signal | Purpose | Confidence Weight |
|--------|---------|-------------------|
| **Vision Transformer (SigLIP)** | Pixel-level synthetic artifact detection | 0–100% |
| **C2PA Manifest Check** | Digital provenance & content credentials | +97% if AI signature found |
| **EXIF / XMP Metadata Scan** | Generator tool keyword detection | +95% if found |
| **Perceptual Hash (dHash)** | Known synthetic sample matching | Up to +92% |

---

## 🖥️ Screenshots

### Dashboard Overview
The main dashboard shows real-time scan stats alongside the Provenance Evidence Scanner.

> Run locally with `python run.py` and navigate to `http://127.0.0.1:8000`

### Evidence Report Panel
Each scan produces a detailed **Evidence Pipeline** breakdown showing:
- **VERDICT**: AI Generated / Real Image
- **CONFIDENCE**: Aggregated multi-signal score
- **C2PA Manifest**, **EXIF/XMP Tags**, **pHash DB**, **Model Score** — each step fully transparent

---

## 🔬 System Architecture

```
User uploads image
        │
        ▼
┌────────────────────────────────────────────┐
│              FastAPI Backend               │
│                                            │
│  ┌──────────────┐  ┌──────────────────┐   │
│  │ EXIF/XMP     │  │ C2PA Manifest    │   │
│  │ Metadata Scan│  │ Checker          │   │
│  └──────────────┘  └──────────────────┘   │
│  ┌──────────────┐  ┌──────────────────┐   │
│  │ pHash dHash  │  │ SigLIP Vision    │   │
│  │ DB Lookup    │  │ Transformer      │   │
│  └──────────────┘  └──────────────────┘   │
│                                            │
│         ▼  Signal Fusion Engine  ▼         │
│     Final Confidence Score + Verdict       │
└────────────────────────────────────────────┘
        │
        ▼
  HTML5 Dashboard (static/index.html)
```

---

## ⚙️ Technology Stack

| Layer | Technology |
|-------|-----------|
| **Backend** | Python 3.11, FastAPI, Uvicorn |
| **ML Model** | `Ateeqq/ai-vs-human-image-detector` (SigLIP Vision Transformer) |
| **Image Processing** | Pillow (PIL), perceptual dHash |
| **Frontend** | HTML5, CSS3 (Glassmorphism Dark UI), Vanilla JavaScript |
| **Auth** | Bearer token sessions |

---

## 🚀 Local Setup & Launch

### Prerequisites
- Python **3.11+**
- pip
- ~3GB free disk (for PyTorch + model cache, downloaded once on first run)

### Step 1 — Clone the Repository
```bash
git clone https://github.com/PrateekGupta786/Truthify.git
cd Truthify
```

### Step 2 — Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 3 — Start the Application
```bash
python run.py
```

### Step 4 — Open in Browser
```
http://127.0.0.1:8000
```

**Login credentials:**
| Field | Value |
|-------|-------|
| Username | `admin` |
| Password | `password` |

> ⏳ **First launch only**: The AI model (~2GB) will auto-download from Hugging Face. This takes 2–5 minutes depending on your internet speed. Subsequent launches are instant.

---

## 📡 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/login` | POST | Authenticate & get bearer token |
| `/api/analyze/file` | POST | Analyze uploaded image file |
| `/api/analyze/url` | POST | Analyze image from URL |
| `/api/stats` | GET | Dashboard scan statistics |
| `/api/history` | GET | Scan history |
| `/api/library` | GET | Reference hash database |
| `/api/library/add` | POST | Save fingerprint to DB |
| `/api/health` | GET | Backend status & model readiness |

### Quick Health Check
```bash
curl http://127.0.0.1:8000/api/health
```
Expected response when model is ready:
```json
{
  "status": "ok",
  "model_ready": true,
  "model_id": "Ateeqq/ai-vs-human-image-detector"
}
```

---

## 📁 Repository Structure

```
Truthify/
├── main.py                      # FastAPI backend, detection logic & all API routes
├── run.py                       # Local dev server launcher
├── requirements.txt             # Python dependencies
├── Truthify_Edunet_Project.pptx # Edunet Foundation capstone presentation
├── data/
│   └── reference_hashes.json   # pHash reference database (auto-created)
└── static/
    └── index.html               # Frontend dashboard UI (served by FastAPI)
```

---

## 🔐 Default Credentials

| Username | Password |
|----------|----------|
| `admin`  | `password` |

To change credentials, set environment variables before running:
```bash
# Windows (PowerShell)
$env:LOGIN_USERNAME="yourname"; $env:LOGIN_PASSWORD="yourpassword"
python run.py

# Linux/macOS
LOGIN_USERNAME=yourname LOGIN_PASSWORD=yourpassword python run.py
```

---

## 🐛 Troubleshooting

**Model download is slow / times out**
```bash
# Increase timeout before running
$env:HF_HUB_TIMEOUT=900
python run.py
```

**Port 8000 already in use**
```bash
# Kill the process using port 8000
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

**`torch` installation fails**
```bash
# Install CPU-only torch manually first
pip install torch --index-url https://download.pytorch.org/whl/cpu
pip install -r requirements.txt
```

---

## 📜 References

1. Zhai, X., et al. (2023). *SigLIP: Sigmoid Loss for Language-Image Pre-Training*. arXiv:2303.15343
2. Ateeqq AI Image Detector: https://huggingface.co/Ateeqq/ai-vs-human-image-detector
3. C2PA Specification v1.3: https://c2pa.org/
4. FastAPI Documentation: https://fastapi.tiangolo.com/
5. PyTorch: https://pytorch.org/

---

*Submitted as part of the Edunet Foundation AI/ML Internship Capstone Project.*
