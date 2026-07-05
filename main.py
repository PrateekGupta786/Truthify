from __future__ import annotations

import io
import json
import secrets
import time
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

from fastapi import FastAPI, File, Header, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from PIL import Image, ImageOps, UnidentifiedImageError
import torch
from transformers import AutoImageProcessor, SiglipForImageClassification

RESAMPLE_LANCZOS = getattr(getattr(Image, "Resampling", Image), "LANCZOS", Image.BICUBIC)


MODEL_ID = "Ateeqq/ai-vs-human-image-detector"
LOGIN_USERNAME = "admin"
LOGIN_PASSWORD = "password"
GENERATOR_HINTS = [
    ("midjourney", "Midjourney"),
    ("stable diffusion", "Stable Diffusion"),
    ("dall-e", "DALL·E"),
    ("dalle", "DALL·E"),
    ("firefly", "Adobe Firefly"),
    ("leonardo", "Leonardo AI"),
    ("runway", "Runway"),
    ("canva", "Canva AI"),
    ("comfyui", "ComfyUI"),
    ("invokeai", "InvokeAI"),
    ("automatic1111", "AUTOMATIC1111"),
    ("fooocus", "Fooocus"),
    ("novelai", "NovelAI"),
    ("ideogram", "Ideogram"),
    ("flux", "FLUX"),
    ("generative", "Generative AI"),
]

C2PA_TOKENS = ["c2pa", "jumbf", "content credentials"]
DB_PATH = Path("data") / "reference_hashes.json"


app = FastAPI(title="Truthify")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:8000",
        "http://localhost:8000",
        "http://localhost:8888",
    ],
    allow_origin_regex=r"https://.*\.netlify\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.mount("/static", StaticFiles(directory="static"), name="static")

app.state.detector = None
app.state.processor = None
app.state.device = None
app.state.model_ready = False
app.state.model_error = None
app.state.sessions = {}
app.state.reference_db = []
app.state.stats = {
    "images_scanned": 0,
    "ai_detected": 0,
    "real_images": 0,
    "confidence_sum": 0.0,
}
app.state.history = []
app.state.notifications = []
app.state.settings = {"name": "Admin User"}


def _make_avatar_data_uri(name: str) -> str:
    initials = "".join(part[:1] for part in name.split()[:2]).upper() or "T"
    svg = f"""
    <svg xmlns="http://www.w3.org/2000/svg" width="128" height="128" viewBox="0 0 128 128">
      <defs>
        <linearGradient id="g" x1="0" x2="1" y1="0" y2="1">
          <stop offset="0%" stop-color="#2563eb"/>
          <stop offset="100%" stop-color="#0f172a"/>
        </linearGradient>
      </defs>
      <rect width="128" height="128" rx="64" fill="url(#g)"/>
      <circle cx="64" cy="52" r="24" fill="rgba(255,255,255,0.92)"/>
      <path d="M26 112c8-20 24-30 38-30s30 10 38 30" fill="rgba(255,255,255,0.92)"/>
      <text x="64" y="74" font-family="Arial, sans-serif" font-size="28" font-weight="700" text-anchor="middle" fill="#0f172a">{initials}</text>
    </svg>
    """.strip()
    return "data:image/svg+xml;utf8," + urllib.parse.quote(svg)


def _build_user_payload() -> dict[str, Any]:
    name = app.state.settings.get("name", "Admin User")
    return {"name": name, "role": "Capstone Reviewer", "avatar": _make_avatar_data_uri(name)}


def _ensure_authenticated(auth_header: Optional[str]) -> dict[str, Any]:
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Unauthorized")
    token = auth_header.removeprefix("Bearer ").strip()
    user = app.state.sessions.get(token)
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return user


def _ensure_data_dir() -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)


def _load_reference_db() -> None:
    _ensure_data_dir()
    if not DB_PATH.exists():
        DB_PATH.write_text("[]", encoding="utf-8")
        app.state.reference_db = []
        return
    try:
        app.state.reference_db = json.loads(DB_PATH.read_text(encoding="utf-8"))
    except Exception:
        app.state.reference_db = []


def _save_reference_db() -> None:
    _ensure_data_dir()
    DB_PATH.write_text(json.dumps(app.state.reference_db, indent=2), encoding="utf-8")


def _load_image_from_bytes(image_bytes: bytes) -> Image.Image:
    try:
        image = Image.open(io.BytesIO(image_bytes))
        return ImageOps.exif_transpose(image).convert("RGB")
    except UnidentifiedImageError as exc:
        raise HTTPException(status_code=400, detail="Unsupported image file.") from exc


def _decode_blob(image_bytes: bytes) -> str:
    return image_bytes.decode("utf-8", errors="ignore").lower()


def _text_hits(text: str) -> list[str]:
    hits = []
    for needle, label in GENERATOR_HINTS:
        if needle in text:
            hits.append(label)
    return hits


def _extract_xmp_text(image: Image.Image, raw_text: str) -> str:
    pieces = [raw_text]
    for key, value in getattr(image, "info", {}).items():
        if isinstance(value, bytes):
            pieces.append(value.decode("utf-8", errors="ignore"))
        else:
            pieces.append(str(value))
    return "\n".join(pieces).lower()


def _compute_dhash(image: Image.Image, hash_size: int = 8) -> str:
    resized = ImageOps.exif_transpose(image).convert("L").resize((hash_size + 1, hash_size), RESAMPLE_LANCZOS)
    pixels = list(resized.getdata())
    bits = 0
    for row in range(hash_size):
        row_start = row * (hash_size + 1)
        for col in range(hash_size):
            left = pixels[row_start + col]
            right = pixels[row_start + col + 1]
            bits = (bits << 1) | int(left > right)
    return f"{bits:016x}"


def _hamming_distance(hash_a: str, hash_b: str) -> int:
    return (int(hash_a, 16) ^ int(hash_b, 16)).bit_count()


def _find_best_reference_match(signature: str) -> Optional[dict[str, Any]]:
    best = None
    for entry in app.state.reference_db:
        entry_signature = entry.get("signature")
        if not entry_signature:
            continue
        try:
            distance = _hamming_distance(signature, entry_signature)
        except Exception:
            continue
        if best is None or distance < best["distance"]:
            best = {
                "id": entry.get("id"),
                "label": entry.get("label", "unknown"),
                "name": entry.get("name", entry.get("source", "Reference sample")),
                "note": entry.get("note", ""),
                "signature": entry_signature,
                "distance": distance,
            }
    if best and best["distance"] <= 12:
        return best
    return None


def _load_model() -> None:
    try:
        print("\nStarting Truthify detector load...")
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        processor = AutoImageProcessor.from_pretrained(MODEL_ID)
        detector = SiglipForImageClassification.from_pretrained(MODEL_ID)
        detector.to(device)
        detector.eval()
        app.state.device = device
        app.state.processor = processor
        app.state.detector = detector
        app.state.model_ready = True
        app.state.model_error = None
        print(f"Model ready on {device}: {MODEL_ID}")
    except Exception as exc:
        app.state.model_ready = False
        app.state.model_error = str(exc)
        print(f"Model load failed, using heuristic fallback: {exc}")


def _ai_label_index(id2label: dict[Any, Any]) -> int:
    best_index = 0
    for raw_index, raw_label in id2label.items():
        index = int(raw_index)
        label = str(raw_label).strip().lower()
        if label in {"ai", "art", "generated", "fake"} or "ai" in label:
            return index
        best_index = index
    return best_index


def _extract_metadata_signals(image: Image.Image, raw_bytes: bytes, source_name: str) -> dict[str, Any]:
    raw_text = _decode_blob(raw_bytes)
    xmp_text = _extract_xmp_text(image, raw_text)
    exif = image.getexif()
    exif_map = {}
    for tag_id, value in exif.items():
        exif_map[str(tag_id)] = str(value)

    software = str(exif.get(305, image.info.get("software", "")) or image.info.get("Software", "")).strip()
    creator_tool = str(image.info.get("CreatorTool", image.info.get("creator_tool", "")) or "").strip()
    generator_hits = _text_hits(" ".join([xmp_text, software.lower(), creator_tool.lower()]))
    c2pa_found = any(token in raw_text for token in C2PA_TOKENS)
    c2pa_evidence = []
    if c2pa_found:
        c2pa_evidence.append("Embedded C2PA-like provenance markers found")
    if generator_hits:
        c2pa_evidence.append("Generator keywords found in metadata")

    if c2pa_found and generator_hits:
        c2pa_status = "Found AI signature"
    elif c2pa_found:
        c2pa_status = "Manifest present"
    else:
        c2pa_status = "No manifest found"

    xmp_keywords = generator_hits[:]
    metadata_hits = []
    if software:
        metadata_hits.append(f"Software: {software}")
    if creator_tool and creator_tool.lower() != software.lower():
        metadata_hits.append(f"Creator tool: {creator_tool}")
    if xmp_keywords:
        metadata_hits.extend(xmp_keywords)

    search_terms = []
    if xmp_keywords:
        search_terms.extend(xmp_keywords)
    if software:
        search_terms.append(software)
    if creator_tool:
        search_terms.append(creator_tool)
    if not search_terms:
        search_terms.extend([source_name, "AI image provenance check"])

    return {
        "exif_count": len(exif),
        "software": software or "Unknown",
        "creator_tool": creator_tool or "Unknown",
        "xmp_keywords": xmp_keywords,
        "metadata_hits": metadata_hits,
        "c2pa": {
            "found": c2pa_found,
            "status": c2pa_status,
            "evidence": c2pa_evidence,
        },
        "search_terms": search_terms,
        "exif_summary": "No EXIF data" if not exif else f"{len(exif)} EXIF tags",
        "raw_text": xmp_text,
    }


def _model_probability(image: Image.Image) -> tuple[Optional[float], dict[str, Any]]:
    if not app.state.model_ready or app.state.detector is None or app.state.processor is None:
        return None, {"available": False, "label": "Model unavailable", "source": "heuristic fallback"}

    inputs = app.state.processor(images=image, return_tensors="pt")
    inputs = {key: value.to(app.state.device) for key, value in inputs.items()}
    with torch.no_grad():
        outputs = app.state.detector(**inputs)
    probabilities = torch.softmax(outputs.logits, dim=-1)[0]
    id2label = app.state.detector.config.id2label
    ai_index = _ai_label_index(id2label)
    ai_score = float(probabilities[ai_index].item()) * 100.0
    top_index = int(torch.argmax(probabilities).item())
    top_label = str(id2label.get(top_index, "Unknown"))
    return ai_score, {
        "available": True,
        "label": top_label,
        "top_score": round(float(probabilities[top_index].item()) * 100.0, 2),
        "ai_label": str(id2label.get(ai_index, "AI")),
        "source": MODEL_ID,
    }


def _score_from_signals(model_ai: Optional[float], metadata: dict[str, Any], phash_match: Optional[dict[str, Any]]) -> tuple[float, list[str], list[dict[str, Any]], dict[str, Any]]:
    evidence = []
    steps = []
    ai_score = 50.0 if model_ai is None else float(model_ai)
    model_available = model_ai is not None

    c2pa = metadata["c2pa"]
    if c2pa["status"] == "Found AI signature":
        ai_score = max(ai_score, 97.0)
        evidence.append("C2PA provenance suggests synthetic content")
        steps.append({"step": "Check C2PA Manifest", "status": "found", "detail": c2pa["status"]})
    elif c2pa["status"] == "Manifest present":
        ai_score = max(ai_score, 68.0)
        evidence.append("C2PA manifest present, but no explicit authenticity claim")
        steps.append({"step": "Check C2PA Manifest", "status": "present", "detail": c2pa["status"]})
    else:
        steps.append({"step": "Check C2PA Manifest", "status": "none", "detail": c2pa["status"]})

    if metadata["xmp_keywords"]:
        ai_score = max(ai_score, 95.0)
        evidence.append("XMP/EXIF metadata contains generator keywords")
        steps.append({"step": "Scrape EXIF/XMP Tags", "status": "found", "detail": ", ".join(metadata["xmp_keywords"])})
    elif metadata["exif_count"] == 0:
        ai_score = max(ai_score, 55.0)
        steps.append({"step": "Scrape EXIF/XMP Tags", "status": "clean", "detail": metadata["exif_summary"]})
    else:
        steps.append({"step": "Scrape EXIF/XMP Tags", "status": "clean", "detail": metadata["exif_summary"]})

    hash_signal = 50.0
    if phash_match:
        label = str(phash_match.get("label", "unknown")).lower()
        distance = int(phash_match.get("distance", 99))
        if label in {"fake", "synthetic", "ai", "generated"}:
            hash_signal = max(92.0, 100.0 - distance * 2)
            ai_score = max(ai_score, hash_signal)
            evidence.append(f"Perceptual hash matched known fake sample ({distance} bits away)")
            steps.append({"step": "Query pHash DB", "status": "match", "detail": f"{phash_match['name']} ({distance} bits)"})
        else:
            hash_signal = min(10.0, distance * 1.5)
            ai_score = min(ai_score, hash_signal)
            evidence.append(f"Perceptual hash matched known real sample ({distance} bits away)")
            steps.append({"step": "Query pHash DB", "status": "match", "detail": f"{phash_match['name']} ({distance} bits)"})
    else:
        steps.append({"step": "Query pHash DB", "status": "no match", "detail": "No close reference found"})

    if model_available:
        steps.append({"step": "Model Score", "status": "ready", "detail": f"Model probability {model_ai:.2f}%"})
    else:
        steps.append({"step": "Model Score", "status": "fallback", "detail": "Using metadata and hash checks"})

    if not evidence and model_available:
        ai_score = max(0.0, min(100.0, float(model_ai)))
    elif not evidence and not model_available:
        ai_score = 45.0

    ai_score = round(max(0.0, min(100.0, ai_score)), 2)
    verdict = "AI Generated" if ai_score >= 50.0 else "Real Image"
    generator = metadata["xmp_keywords"][0] if metadata["xmp_keywords"] else (metadata["software"] if metadata["software"] != "Unknown" else "None")
    return ai_score, evidence, steps, {"generator": generator, "hash_signal": hash_signal, "verdict": verdict}


def _normalize_query_terms(terms: list[str]) -> str:
    cleaned = []
    for term in terms:
        term = str(term).strip()
        if term and term.lower() not in {x.lower() for x in cleaned}:
            cleaned.append(term)
    if not cleaned:
        cleaned = ["AI image provenance", "reverse image check"]
    return " ".join(cleaned[:4])


def _make_analysis(image: Image.Image, raw_bytes: bytes, source_name: str) -> dict[str, Any]:
    started = time.perf_counter()
    model_ai, model_info = _model_probability(image)
    metadata = _extract_metadata_signals(image, raw_bytes, source_name)
    signature = _compute_dhash(image)
    reference_match = _find_best_reference_match(signature)
    ai_score, evidence, steps, score_meta = _score_from_signals(model_ai, metadata, reference_match)
    elapsed = round((time.perf_counter() - started) * 1000.0)

    prediction = "AI Generated" if ai_score >= 50.0 else "Real Image"
    threat_level = "High" if ai_score >= 80.0 else "Medium" if ai_score >= 50.0 else "Low"
    detected_artifacts = evidence[:] if evidence else ["No strong provenance issues detected"]
    if prediction == "Real Image" and not evidence:
        detected_artifacts = ["No C2PA abuse detected", "No suspicious XMP keywords", "No pHash match"]

    c2pa = metadata["c2pa"]
    xmp_summary = metadata["xmp_keywords"] if metadata["xmp_keywords"] else ["None"]
    phash_summary = {
        "signature": signature,
        "match_found": bool(reference_match),
        "match_name": reference_match["name"] if reference_match else "No close match",
        "match_label": reference_match["label"] if reference_match else "Unknown",
        "distance": reference_match["distance"] if reference_match else None,
    }

    confidence = ai_score
    real_confidence = round(100.0 - ai_score, 2)

    return {
        "prediction": prediction,
        "confidence": confidence,
        "confidence_score": confidence,
        "real_confidence": real_confidence,
        "model_probability": None if model_ai is None else round(model_ai, 2),
        "combined_ai_probability": ai_score,
        "generator": score_meta["generator"],
        "inference_time": f"{elapsed} ms",
        "metadata": {
            "format": image.format or "Unknown",
            "dimensions": f"{image.width} x {image.height}",
            "exif_anomalies": metadata["exif_summary"],
            "software": metadata["software"],
            "creator_tool": metadata["creator_tool"],
            "exif_count": metadata["exif_count"],
        },
        "signals": {
            "model": model_info,
            "c2pa": c2pa,
            "xmp": {"keywords": xmp_summary, "hits": metadata["metadata_hits"]},
            "phash": phash_summary,
        },
        "analysis_chain": steps,
        "detected_artifacts": detected_artifacts,
        "threat_level": threat_level,
        "signature": signature,
        "source_name": source_name,
        "evidence": evidence,
    }


def _store_analysis(name: str, image_type: str, result: dict[str, Any]) -> None:
    app.state.stats["images_scanned"] += 1
    app.state.stats["confidence_sum"] += result["confidence"]
    if result["prediction"] == "AI Generated":
        app.state.stats["ai_detected"] += 1
    else:
        app.state.stats["real_images"] += 1

    app.state.history.insert(
        0,
        {
            "media": name,
            "type": image_type,
            "prob": result["confidence"],
            "gen": result["generator"],
            "status": "Deepfake" if result["prediction"] == "AI Generated" else "Authentic",
            "prediction": result["prediction"],
            "threat_level": result["threat_level"],
        },
    )

    notice_text = (
        f"{name} flagged as AI generated with {result['confidence']}% confidence."
        if result["prediction"] == "AI Generated"
        else f"{name} appears authentic."
    )
    app.state.notifications.insert(0, {"text": notice_text, "read": False})
    app.state.notifications = app.state.notifications[:20]
    app.state.history = app.state.history[:20]


def _read_body_json(payload: dict[str, Any], key: str, default: str = "") -> str:
    value = payload.get(key, default)
    return str(value).strip()


@app.on_event("startup")
async def startup_event() -> None:
    _load_reference_db()
    _load_model()


@app.get("/")
async def read_index() -> FileResponse:
    return FileResponse("static/index.html")


@app.post("/api/login")
async def login(payload: dict[str, Any]) -> dict[str, str]:
    username = _read_body_json(payload, "username")
    password = _read_body_json(payload, "password")
    if username != LOGIN_USERNAME or password != LOGIN_PASSWORD:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = secrets.token_urlsafe(32)
    app.state.sessions[token] = _build_user_payload()
    return {"token": token}


@app.get("/api/me")
async def me(authorization: Optional[str] = Header(None)) -> dict[str, Any]:
    return _ensure_authenticated(authorization)


@app.get("/api/stats")
async def stats(authorization: Optional[str] = Header(None)) -> dict[str, Any]:
    _ensure_authenticated(authorization)
    scanned = app.state.stats["images_scanned"]
    avg = 0.0 if scanned == 0 else app.state.stats["confidence_sum"] / scanned
    return {
        "images_scanned": scanned,
        "ai_detected": app.state.stats["ai_detected"],
        "real_images": app.state.stats["real_images"],
        "avg_confidence": f"{avg:.1f}%" if scanned else "0%",
        "reference_samples": len(app.state.reference_db),
    }


@app.get("/api/history")
async def history(authorization: Optional[str] = Header(None)) -> list[dict[str, Any]]:
    _ensure_authenticated(authorization)
    return app.state.history


@app.get("/api/notifications")
async def notifications(authorization: Optional[str] = Header(None)) -> list[dict[str, Any]]:
    _ensure_authenticated(authorization)
    return app.state.notifications


@app.post("/api/notifications/clear")
async def clear_notifications(authorization: Optional[str] = Header(None)) -> dict[str, str]:
    _ensure_authenticated(authorization)
    app.state.notifications = []
    return {"message": "Notifications cleared"}


@app.post("/api/settings/update")
async def update_settings(payload: dict[str, Any], authorization: Optional[str] = Header(None)) -> dict[str, Any]:
    _ensure_authenticated(authorization)
    name = _read_body_json(payload, "name")
    if name:
        app.state.settings["name"] = name
    return {"message": "Settings updated", "name": app.state.settings["name"]}


@app.post("/api/actions/{action_type}")
async def actions(action_type: str, authorization: Optional[str] = Header(None)) -> dict[str, str]:
    _ensure_authenticated(authorization)
    messages = {
        "report": "Incident report prepared",
        "download": "Download started",
        "share": "Share link copied",
    }
    return {"message": messages.get(action_type, "Action completed")}


@app.post("/api/library/add")
async def library_add(payload: dict[str, Any], authorization: Optional[str] = Header(None)) -> dict[str, Any]:
    _ensure_authenticated(authorization)
    signature = _read_body_json(payload, "signature")
    label = _read_body_json(payload, "label", "fake").lower() or "fake"
    name = _read_body_json(payload, "name", "Reference sample")
    note = _read_body_json(payload, "note", "")
    if not signature:
        raise HTTPException(status_code=400, detail="Signature is required")

    entry = {
        "id": secrets.token_hex(8),
        "signature": signature,
        "label": label,
        "name": name,
        "note": note,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    app.state.reference_db.insert(0, entry)
    app.state.reference_db = app.state.reference_db[:500]
    _save_reference_db()
    return {"message": "Reference sample saved", "entry": entry, "count": len(app.state.reference_db)}


@app.get("/api/library")
async def library(authorization: Optional[str] = Header(None)) -> dict[str, Any]:
    _ensure_authenticated(authorization)
    return {"count": len(app.state.reference_db), "items": app.state.reference_db}


@app.post("/api/analyze/file")
async def analyze_file(file: UploadFile = File(...)) -> dict[str, Any]:
    raw_bytes = await file.read()
    image = _load_image_from_bytes(raw_bytes)
    result = _make_analysis(image, raw_bytes, file.filename or "uploaded-image")
    _store_analysis(file.filename or "uploaded-image", "Image", result)
    return result


@app.post("/api/analyze/url")
async def analyze_url(payload: dict[str, Any]) -> dict[str, Any]:
    url = _read_body_json(payload, "url")
    if not url:
        raise HTTPException(status_code=400, detail="Image URL is required.")

    parsed = urllib.parse.urlparse(url)
    if parsed.scheme not in {"http", "https"}:
        raise HTTPException(status_code=400, detail="Only http and https URLs are allowed.")

    try:
        with urllib.request.urlopen(url, timeout=20) as response:
            raw_bytes = response.read()
    except Exception as exc:
        raise HTTPException(status_code=400, detail="Could not fetch image URL.") from exc

    image = _load_image_from_bytes(raw_bytes)
    result = _make_analysis(image, raw_bytes, url)
    _store_analysis(url, "URL", result)
    return result


@app.get("/api/health")
async def health() -> dict[str, Any]:
    return {
        "status": "ok",
        "model_ready": app.state.model_ready,
        "model_error": app.state.model_error,
        "model_id": MODEL_ID,
        "reference_samples": len(app.state.reference_db),
    }
