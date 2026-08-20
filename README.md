# 🛡️ Truthify — AI Content Protection Platform

**Edunet Foundation Capstone Internship Project**

Truthify is a hybrid AI media authenticity detection platform that combines a **Vision Transformer (SigLIP)**, C2PA provenance checking, EXIF/XMP metadata scanning, and perceptual hashing (dHash) to identify AI-generated and synthetic images with high confidence.

Live Demo: [![Streamlit App](https://truthify-caumredxytappbjgccvnxqo.streamlit.app/)](https://truthify.streamlit.app)

---

##  How It Works

Each uploaded image is passed through a **multi-signal evidence pipeline**:

1. **SigLIP Vision Transformer** — Deep learning classification (AI Generated vs Real)
2. **C2PA Manifest Check** — Detects embedded content credentials from AI tools
3. **EXIF / XMP Metadata Scan** — Identifies generator keywords (Midjourney, DALL-E, etc.)
4. **Perceptual Hash (dHash)** — Matches against a reference database of known synthetic samples

All signals are fused into a single confidence score and verdict.

---

##  Live Demo

Try it instantly — no install required:

👉 **[https://truthify.streamlit.app](https://truthify.streamlit.app)**

> ⏳ First load downloads the AI model (~2GB). Subsequent runs are instant thanks to Streamlit's resource caching.

---

##  Getting Started (Local)

### Requirements
- Python 3.11+
- ~3GB disk space (AI model auto-downloads once on first run)

### Install & Run

```bash
git clone https://github.com/PrateekGupta786/Truthify.git
cd Truthify
pip install -r requirements.txt
```

**Option A — Streamlit UI (recommended)**
```bash
streamlit run streamlit_app.py
```
Opens automatically in your browser at `http://localhost:8501`.

**Option B — Web Dashboard (FastAPI)**
```bash
python run.py
```
Open **[http://127.0.0.1:8000](http://127.0.0.1:8000)** · Login: `admin` / `password`

> ⏳ First launch downloads the AI model (~2GB). Takes 2–5 minutes. Subsequent launches are instant.

---

## 🔐 Credentials (FastAPI Dashboard only)

| Username | Password |
|----------|----------|
| `admin`  | `password` |

---

## 📁 Project Structure

```
Truthify/
├── streamlit_app.py     # Streamlit UI (primary interface & Streamlit Cloud entry point)
├── main.py              # FastAPI backend & detection logic
├── run.py               # Local FastAPI server launcher
├── requirements.txt     # Python dependencies
├── .streamlit/
│   └── config.toml      # Streamlit Cloud theme & server config
├── static/
│   └── index.html       # FastAPI web dashboard UI
└── data/
    └── reference_hashes.json   # Known AI image perceptual hash database
```

---


