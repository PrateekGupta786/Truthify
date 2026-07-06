"""
Truthify - Multi-Agent AI Detection System
==========================================

Architecture: Agent Orchestrator Pattern
- Coordinator Agent: Routes analysis tasks to specialized agents
- Metadata Agent: Analyzes EXIF/XMP metadata
- Hash Agent: Performs perceptual hash matching
- Model Agent: Runs Vision Transformer inference
- Report Agent: Generates analysis reports

This implementation demonstrates multi-agent collaboration for AI content detection.
"""

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import torch
from transformers import AutoImageProcessor, SiglipForImageClassification
from PIL import Image
import io
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
import secrets
from datetime import datetime, timezone
import urllib.parse

# ============================================================================
# AGENT 1: METADATA ANALYSIS AGENT
# ============================================================================
class MetadataAgent:
    """
    Specialized agent for analyzing image metadata signals.
    Responsible for: EXIF/XMP extraction, generator keyword detection, C2PA inspection
    """
    
    def __init__(self):
        self.name = "MetadataAgent"
        self.tools = ["extract_exif", "scan_xmp", "detect_generators", "check_c2pa"]
    
    def analyze(self, image: Image.Image, raw_bytes: bytes) -> Dict[str, Any]:
        """Execute metadata analysis task"""
        exif = image.getexif()
        raw_text = raw_bytes.decode("utf-8", errors="ignore").lower()
        
        # Tool: extract_exif
        exif_data = {str(k): str(v) for k, v in exif.items()}
        
        # Tool: scan_xmp
        xmp_data = image.info
        
        # Tool: detect_generators
        generator_keywords = [
            "midjourney", "stable diffusion", "dall-e", "firefly",
            "leonardo", "runway", "canva", "comfyui"
        ]
        detected = [kw for kw in generator_keywords if kw in raw_text]
        
        # Tool: check_c2pa
        c2pa_tokens = ["c2pa", "jumbf", "content credentials"]
        c2pa_found = any(token in raw_text for token in c2pa_tokens)
        
        return {
            "agent": self.name,
            "exif_count": len(exif),
            "detected_generators": detected,
            "c2pa_found": c2pa_found,
            "metadata_score": 95.0 if detected else (85.0 if c2pa_found else 0.0)
        }


# ============================================================================
# AGENT 2: PERCEPTUAL HASH AGENT
# ============================================================================
class HashAgent:
    """
    Specialized agent for perceptual hash matching and reference database queries.
    Responsible for: dhash computation, similarity matching, known sample detection
    """
    
    def __init__(self, db_path: Path):
        self.name = "HashAgent"
        self.db_path = db_path
        self.tools = ["compute_hash", "query_database", "match_similarity"]
        self._load_database()
    
    def _load_database(self):
        """Load reference hash database"""
        if self.db_path.exists():
            self.reference_db = json.loads(self.db_path.read_text())
        else:
            self.reference_db = []
    
    def compute_dhash(self, image: Image.Image, hash_size: int = 8) -> str:
        """Tool: compute_hash - Generate perceptual hash"""
        resized = image.convert("L").resize((hash_size + 1, hash_size))
        pixels = list(resized.getdata())
        bits = 0
        for row in range(hash_size):
            for col in range(hash_size):
                left = pixels[row * (hash_size + 1) + col]
                right = pixels[row * (hash_size + 1) + col + 1]
                bits = (bits << 1) | int(left > right)
        return f"{bits:016x}"
    
    def analyze(self, image: Image.Image) -> Dict[str, Any]:
        """Execute hash-based analysis task"""
        # Tool: compute_hash
        signature = self.compute_dhash(image)
        
        # Tool: query_database
        match = None
        for entry in self.reference_db:
            entry_hash = entry.get("signature")
            if entry_hash:
                distance = bin(int(signature, 16) ^ int(entry_hash, 16)).count('1')
                if distance <= 12:
                    match = {
                        "name": entry.get("name"),
                        "label": entry.get("label"),
                        "distance": distance
                    }
                    break
        
        # Tool: match_similarity
        hash_score = 92.0 if match and match["label"] == "fake" else (8.0 if match else 0.0)
        
        return {
            "agent": self.name,
            "signature": signature,
            "reference_match": match,
            "hash_score": hash_score
        }


# ============================================================================
# AGENT 3: MODEL INFERENCE AGENT
# ============================================================================
class ModelAgent:
    """
    Specialized agent for Vision Transformer inference.
    Responsible for: Model loading, image classification, probability computation
    """
    
    def __init__(self):
        self.name = "ModelAgent"
        self.tools = ["load_model", "preprocess_image", "run_inference"]
        self.model = None
        self.processor = None
        self.device = None
        self._initialize()
    
    def _initialize(self):
        """Tool: load_model - Initialize Vision Transformer"""
        try:
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
            self.processor = AutoImageProcessor.from_pretrained(
                "Ateeqq/ai-vs-human-image-detector"
            )
            self.model = SiglipForImageClassification.from_pretrained(
                "Ateeqq/ai-vs-human-image-detector"
            )
            self.model.to(self.device)
            self.model.eval()
        except Exception as e:
            print(f"Model initialization failed: {e}")
    
    def analyze(self, image: Image.Image) -> Dict[str, Any]:
        """Execute model inference task"""
        if not self.model:
            return {"agent": self.name, "model_score": 0.0, "available": False}
        
        try:
            # Tool: preprocess_image
            inputs = self.processor(images=image, return_tensors="pt")
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            # Tool: run_inference
            with torch.no_grad():
                outputs = self.model(**inputs)
            
            probabilities = torch.softmax(outputs.logits, dim=-1)[0]
            ai_score = float(probabilities[0].item()) * 100.0
            
            return {
                "agent": self.name,
                "model_score": ai_score,
                "available": True
            }
        except Exception as e:
            return {"agent": self.name, "model_score": 0.0, "available": False, "error": str(e)}


# ============================================================================
# AGENT 4: REPORT GENERATION AGENT
# ============================================================================
class ReportAgent:
    """
    Specialized agent for synthesizing analysis results and generating reports.
    Responsible for: Score aggregation, verdict generation, evidence compilation
    """
    
    def __init__(self):
        self.name = "ReportAgent"
        self.tools = ["aggregate_scores", "generate_verdict", "compile_evidence"]
    
    def synthesize(self, agent_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Execute report synthesis task"""
        # Tool: aggregate_scores
        metadata_score = next((r.get("metadata_score", 0) for r in agent_results 
                              if r.get("agent") == "MetadataAgent"), 0)
        hash_score = next((r.get("hash_score", 0) for r in agent_results 
                          if r.get("agent") == "HashAgent"), 0)
        model_score = next((r.get("model_score", 0) for r in agent_results 
                           if r.get("agent") == "ModelAgent"), 0)
        
        final_score = max(metadata_score, hash_score, model_score) if any([
            metadata_score, hash_score, model_score
        ]) else 50.0
        
        # Tool: generate_verdict
        verdict = "AI Generated" if final_score >= 50 else "Real Image"
        threat_level = "High" if final_score >= 80 else "Medium" if final_score >= 50 else "Low"
        
        # Tool: compile_evidence
        evidence = []
        if metadata_score > 0:
            evidence.append("Metadata signals detected")
        if hash_score > 0:
            evidence.append("Reference database match found")
        if model_score > 0:
            evidence.append("Vision Transformer inference positive")
        
        return {
            "agent": self.name,
            "final_score": round(final_score, 2),
            "verdict": verdict,
            "threat_level": threat_level,
            "evidence": evidence,
            "agent_results": agent_results
        }


# ============================================================================
# COORDINATOR AGENT (ORCHESTRATOR)
# ============================================================================
class CoordinatorAgent:
    """
    Master orchestrator agent that coordinates all specialized agents.
    Implements the multi-agent system pattern for AI detection.
    
    Workflow:
    1. Receive image and request
    2. Dispatch to Metadata Agent
    3. Dispatch to Hash Agent
    4. Dispatch to Model Agent
    5. Synthesize with Report Agent
    6. Return complete analysis
    """
    
    def __init__(self, db_path: Path):
        self.name = "CoordinatorAgent"
        self.agents = {
            "metadata": MetadataAgent(),
            "hash": HashAgent(db_path),
            "model": ModelAgent(),
            "report": ReportAgent()
        }
    
    def orchestrate_analysis(self, image: Image.Image, raw_bytes: bytes) -> Dict[str, Any]:
        """
        Orchestrate multi-agent analysis workflow.
        This is the key function demonstrating multi-agent collaboration.
        """
        
        # Agent 1: Metadata analysis
        metadata_result = self.agents["metadata"].analyze(image, raw_bytes)
        
        # Agent 2: Hash-based analysis
        hash_result = self.agents["hash"].analyze(image)
        
        # Agent 3: Model inference
        model_result = self.agents["model"].analyze(image)
        
        # Synthesize results
        all_results = [metadata_result, hash_result, model_result]
        final_report = self.agents["report"].synthesize(all_results)
        
        return final_report


# ============================================================================
# MAIN APPLICATION
# ============================================================================

RESAMPLE_LANCZOS = getattr(getattr(Image, "Resampling", Image), "LANCZOS", Image.BICUBIC)
MODEL_ID = "Ateeqq/ai-vs-human-image-detector"
LOGIN_USERNAME = "admin"
LOGIN_PASSWORD = "password"
DB_PATH = Path("data") / "reference_hashes.json"

app = FastAPI(
    title="Truthify - Multi-Agent AI Detection System",
    description="Demonstrates multi-agent architecture for AI content detection"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:8000", "http://localhost:8000", "http://localhost:8888"],
    allow_origin_regex=r"https://.*\.netlify\.app|https://huggingface\.co.*",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Initialize coordinator agent (master orchestrator)
coordinator = CoordinatorAgent(DB_PATH)

# Global state
app.state.sessions = {}
app.state.reference_db = []
app.state.stats = {"images_scanned": 0, "ai_detected": 0, "real_images": 0}
app.state.history = []


def _make_avatar_data_uri(name: str) -> str:
    """Generate avatar for user"""
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
      <text x="64" y="74" font-family="Arial" font-size="28" font-weight="700" text-anchor="middle" fill="#0f172a">{initials}</text>
    </svg>
    """
    return "data:image/svg+xml;utf8," + urllib.parse.quote(svg)


@app.get("/")
async def read_index():
    from fastapi.responses import FileResponse
    return FileResponse("static/index.html")


@app.post("/api/login")
async def login(payload: dict):
    """Authenticate user"""
    username = payload.get("username", "").strip()
    password = payload.get("password", "").strip()
    
    if username != LOGIN_USERNAME or password != LOGIN_PASSWORD:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    token = secrets.token_urlsafe(32)
    app.state.sessions[token] = {
        "name": "Admin User",
        "role": "AI Detection Analyst",
        "avatar": _make_avatar_data_uri("Admin User")
    }
    return {"token": token}


@app.get("/api/me")
async def me(authorization: Optional[str] = None):
    """Get current user"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    token = authorization.removeprefix("Bearer ").strip()
    if token not in app.state.sessions:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    return app.state.sessions[token]


@app.post("/api/analyze/file")
async def analyze_file(file: UploadFile = File(...)):
    """
    Analyze uploaded image using multi-agent system.
    
    This endpoint demonstrates the CoordinatorAgent orchestrating
    specialized agents for comprehensive AI detection.
    """
    try:
        raw_bytes = await file.read()
        image = Image.open(io.BytesIO(raw_bytes)).convert("RGB")
        
        # MULTI-AGENT ORCHESTRATION
        result = coordinator.orchestrate_analysis(image, raw_bytes)
        
        # Store analysis in history
        app.state.stats["images_scanned"] += 1
        if result["verdict"] == "AI Generated":
            app.state.stats["ai_detected"] += 1
        else:
            app.state.stats["real_images"] += 1
        
        app.state.history.insert(0, {
            "media": file.filename or "uploaded-image",
            "type": "Image",
            "prediction": result["verdict"],
            "confidence": result["final_score"],
            "threat_level": result["threat_level"]
        })
        
        return result
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Analysis failed: {str(e)}")


@app.get("/api/stats")
async def stats(authorization: Optional[str] = None):
    """Get analysis statistics"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    return {
        "images_scanned": app.state.stats["images_scanned"],
        "ai_detected": app.state.stats["ai_detected"],
        "real_images": app.state.stats["real_images"],
        "agents_active": list(coordinator.agents.keys())
    }


@app.get("/api/history")
async def history(authorization: Optional[str] = None):
    """Get scan history"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    return app.state.history


@app.get("/api/health")
async def health():
    """Health check endpoint"""
    model_ready = coordinator.agents["model"].model is not None
    return {
        "status": "ok",
        "model_ready": model_ready,
        "architecture": "Multi-Agent Orchestrator",
        "agents": list(coordinator.agents.keys()),
        "model_id": MODEL_ID
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7860)
