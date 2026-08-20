---
title: Truthify
emoji: 🛡️
colorFrom: blue
colorTo: gray
sdk: docker
pinned: false
---

# Truthify - AI Content Protection Platform

**Edunet Foundation Capstone Internship Project**

A hybrid AI media authenticity platform combining deep learning (SigLIP Vision Transformer), C2PA provenance checking, EXIF/XMP metadata analysis, and perceptual hashing (dHash) to identify synthetic and AI-generated media.

---

## 🎯 Features

- **Multi-Signal Detection**: Model probability + C2PA manifest + EXIF/XMP keywords + pHash similarity
- **Interactive Dashboard**: Sleek responsive web UI served directly by FastAPI backend
- **Real-Time Inference**: Processes media in <500ms with automatic memory fallback mode on low-resource environments

---

## 🚀 Quick Start (Local Development)

### 1. Clone & Install Dependencies
```bash
git clone https://github.com/PrateekGupta786/Truthify.git
cd Truthify
pip install -r requirements.txt
```

### 2. Run Application
```bash
python run.py
```

Open [http://127.0.0.1:8000](http://127.0.0.1:8000) and login with:
- **Username**: `admin`
- **Password**: `password`

---

## 🔗 Live Deployment

- **Interactive Web Demo**: [https://huggingface.co/spaces/Prateek786/TruthifyAI](https://huggingface.co/spaces/Prateek786/TruthifyAI)

---

## 📁 Repository Structure
```
Truthify/
├── run.py                       # Local FastAPI launcher
├── main.py                      # FastAPI server & detection logic
├── requirements.txt             # Python dependencies
├── Dockerfile                   # Docker configuration for cloud deployment
├── Truthify_Edunet_Project.pptx # Final Presentation Slides
├── data/
│   └── reference_hashes.json
└── static/
    └── index.html               # Frontend dashboard UI
```
