# 🛡️ Truthify — AI Content Protection Platform

**Edunet Foundation Capstone Internship Project**

Truthify is a hybrid AI media authenticity detection platform that combines a **Vision Transformer (SigLIP)**, C2PA provenance checking, EXIF/XMP metadata scanning, and perceptual hashing (dHash) to identify AI-generated and synthetic images with high confidence.

---

## ✨ How It Works

Each uploaded image is passed through a **multi-signal evidence pipeline**:

1. **SigLIP Vision Transformer** — Deep learning classification (AI Generated vs Real)
2. **C2PA Manifest Check** — Detects embedded content credentials from AI tools
3. **EXIF / XMP Metadata Scan** — Identifies generator keywords (Midjourney, DALL-E, etc.)
4. **Perceptual Hash (dHash)** — Matches against a reference database of known synthetic samples

All signals are fused into a single confidence score and verdict.

---

## 🚀 Getting Started

### Requirements
- Python 3.11+
- ~3GB disk space (AI model auto-downloads once on first run)

### Install & Run

```bash
git clone https://github.com/PrateekGupta786/Truthify.git
cd Truthify
pip install -r requirements.txt
```

**Option A — Web Dashboard (FastAPI)**
```bash
python run.py
```
Open **[http://127.0.0.1:8000](http://127.0.0.1:8000)** · Login: `admin` / `password`

**Option B — Streamlit UI**
```bash
streamlit run streamlit_app.py
```
Opens automatically in your browser.

> ⏳ First launch downloads the AI model (~2GB). Takes 2–5 minutes. Subsequent launches are instant.

---

## 🔐 Credentials

| Username | Password |
|----------|----------|
| `admin`  | `password` |

---

## 📁 Project Structure

```
Truthify/
├── main.py          # FastAPI backend & detection logic
├── run.py           # Local server launcher
├── requirements.txt # Dependencies
├── static/
│   └── index.html   # Web dashboard UI
└── data/
    └── reference_hashes.json
```

---

*Submitted as part of the Edunet Foundation AI/ML Internship Capstone Project.*
