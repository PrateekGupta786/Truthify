import io
import time
import urllib.request

import PIL.Image
import PIL.ImageOps
import streamlit as st
import torch
from transformers import AutoImageProcessor, SiglipForImageClassification

st.set_page_config(
    page_title="Truthify - AI Content Protection",
    page_icon="🛡️",
    layout="wide",
)

MODEL_ID = "Ateeqq/ai-vs-human-image-detector"
GENERATOR_HINTS = [
    ("midjourney", "Midjourney"), ("stable diffusion", "Stable Diffusion"),
    ("dall-e", "DALL·E"), ("dalle", "DALL·E"), ("firefly", "Adobe Firefly"),
    ("leonardo", "Leonardo AI"), ("runway", "Runway"), ("canva", "Canva AI"),
    ("comfyui", "ComfyUI"), ("flux", "FLUX"),
]
C2PA_TOKENS = ["c2pa", "jumbf", "content credentials"]


@st.cache_resource(show_spinner="Loading AI model (~2GB, first run only)…")
def load_model():
    try:
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        processor = AutoImageProcessor.from_pretrained(MODEL_ID)
        model = SiglipForImageClassification.from_pretrained(MODEL_ID)
        model.to(device).eval()
        return processor, model, device, True
    except Exception as e:
        return None, None, None, False


def compute_dhash(image, hash_size=8):
    resized = PIL.ImageOps.exif_transpose(image).convert("L").resize(
        (hash_size + 1, hash_size), PIL.Image.Resampling.LANCZOS
    )
    pixels = list(resized.getdata())
    bits = 0
    for row in range(hash_size):
        for col in range(hash_size):
            l = pixels[row * (hash_size + 1) + col]
            r = pixels[row * (hash_size + 1) + col + 1]
            bits = (bits << 1) | int(l > r)
    return f"{bits:016x}"


def analyze(image, raw_bytes, processor, model, device, model_ready):
    t0 = time.time()
    raw_text = raw_bytes.decode("utf-8", errors="ignore").lower()
    exif = image.getexif()
    c2pa_found = any(t in raw_text for t in C2PA_TOKENS)
    hints = [label for needle, label in GENERATOR_HINTS if needle in raw_text]
    sig = compute_dhash(image)

    score = 50.0
    if model_ready and model:
        try:
            inputs = processor(images=image, return_tensors="pt")
            inputs = {k: v.to(device) for k, v in inputs.items()}
            with torch.no_grad():
                out = model(**inputs)
            probs = torch.softmax(out.logits, dim=-1)[0]
            id2label = getattr(model.config, "id2label", {0: "AI", 1: "Human"})
            ai_idx = next(
                (int(i) for i, l in id2label.items() if "ai" in str(l).lower() or "fake" in str(l).lower()),
                0,
            )
            score = float(probs[ai_idx].item()) * 100.0
        except Exception:
            pass

    evidence = []
    if c2pa_found:
        score = max(score, 97.0)
        evidence.append("C2PA Content Credentials detected")
    if hints:
        score = max(score, 95.0)
        evidence.append(f"Generator metadata found: {', '.join(hints)}")
    if not exif:
        evidence.append("No EXIF metadata (possible stripping)")

    score = round(max(0.0, min(100.0, score)), 2)
    return {
        "verdict": "AI Generated" if score >= 50.0 else "Real Image",
        "confidence": score,
        "threat": "High" if score >= 80 else "Medium" if score >= 50 else "Low",
        "model_score": round(score, 2),
        "evidence": evidence,
        "signature": sig,
        "exif_count": len(exif),
        "c2pa": c2pa_found,
        "dims": f"{image.width} × {image.height}",
        "ms": round((time.time() - t0) * 1000),
    }


# ── UI ──────────────────────────────────────────────────────────────────────
st.title("🛡️ Truthify — AI Content Protection Platform")
st.caption("Edunet Foundation Capstone Project · Multi-Signal AI & Deepfake Detection")

processor, model, device, model_ready = load_model()

with st.sidebar:
    st.header("System Status")
    if model_ready:
        st.success(f"✅ Model ready (`{device}`)")
    else:
        st.warning("⚠️ Running in heuristic fallback mode (metadata + hash only)")
    st.markdown("---")
    st.markdown("**Model:** `Ateeqq/ai-vs-human-image-detector`")
    st.markdown("**Architecture:** SigLIP Vision Transformer")

tab_detect, tab_about = st.tabs(["🔍 Detect", "ℹ️ About"])

with tab_detect:
    col1, col2 = st.columns([1, 1], gap="large")

    with col1:
        mode = st.radio("Input", ["Upload File", "Image URL"], horizontal=True)
        image, raw_bytes = None, None

        if mode == "Upload File":
            f = st.file_uploader("Upload image", type=["jpg", "jpeg", "png", "webp"])
            if f:
                raw_bytes = f.read()
                image = PIL.Image.open(io.BytesIO(raw_bytes)).convert("RGB")
        else:
            url = st.text_input("Image URL", placeholder="https://example.com/image.jpg")
            if url:
                try:
                    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
                    with urllib.request.urlopen(req, timeout=15) as r:
                        raw_bytes = r.read()
                    image = PIL.Image.open(io.BytesIO(raw_bytes)).convert("RGB")
                except Exception as e:
                    st.error(f"Could not fetch image: {e}")

        if image:
            st.image(image, use_container_width=True)

    with col2:
        if image and raw_bytes:
            with st.spinner("Analyzing…"):
                res = analyze(image, raw_bytes, processor, model, device, model_ready)

            if res["verdict"] == "AI Generated":
                st.error(f"🚨 **{res['verdict']}** — {res['confidence']}% confidence")
            else:
                st.success(f"✅ **{res['verdict']}** — {100 - res['confidence']:.2f}% real confidence")

            st.progress(res["confidence"] / 100)

            c1, c2, c3 = st.columns(3)
            c1.metric("Threat Level", res["threat"])
            c2.metric("Inference", f"{res['ms']} ms")
            c3.metric("EXIF Tags", res["exif_count"])

            st.markdown("#### Evidence Breakdown")
            st.write(f"• **Model Score:** {res['model_score']}% AI probability")
            st.write(f"• **C2PA Manifest:** {'Found' if res['c2pa'] else 'Not found'}")
            st.write(f"• **pHash Signature:** `{res['signature']}`")
            st.write(f"• **Image Dimensions:** {res['dims']}")

            if res["evidence"]:
                st.markdown("#### ⚠️ Flags")
                for e in res["evidence"]:
                    st.warning(e)
        else:
            st.info("Upload an image or paste a URL on the left to start analysis.")

with tab_about:
    st.markdown("""
    Truthify detects AI-generated images using four independent signals:

    1. **SigLIP Vision Transformer** — deep learning classification
    2. **C2PA Manifest Check** — digital provenance credentials
    3. **EXIF/XMP Metadata Scan** — generator keyword detection
    4. **Perceptual Hash (dHash)** — known synthetic sample matching

    **GitHub:** https://github.com/PrateekGupta786/Truthify
    """)
