🛡️ Truthify AI: Autonomous Multi-Agent Media Forensics Engine
Subtitle: Enterprise Deepfake & Synthetic Media Auditing via Asynchronous Model Context Protocol (MCP) and Multi-Agent Orchestration

📋 Project Overview & Problem Statement
   In the modern digital landscape, the explosion of generative AI and hyper-realistic diffusion models has made verifying visual media a critical challenge for enterprises, newsrooms, and security platforms. Fraudulent identity verification documents (KYC), deepfake imagery in insurance claims, and state-sponsored misinformation campaigns threaten digital trust. Human reviewers cannot catch sub-visual anomalies like micro-spatial inconsistencies or localized tensor fluctuations.Truthify AI solves this problem by transforming deepfake detection from a static command-line classification task into an autonomous, multi-agent security audit. Utilizing a cutting-edge SigLIP (Sigmoid Language-Image Pre-training) Vision Transformer Engine, Truthify AI acts as an enterprise-grade digital notary. It breaks down an image, inspects its core cryptographic, structural, and behavioral properties, and provides structured compliance verdicts.🧠 Core Architecture & Multi-Agent DesignTruthify AI is engineered using an asynchronous Multi-Agent System (MAS) pattern designed with an Agent Development Kit (ADK) wrapper layout. Rather than relying on a single monolith, the platform coordinates five specialized, autonomous agents that manage independent tasks and leverage 13 distinct tools shared via a Model Context Protocol (MCP) structure.     
   [ Web Interface / Client Request ]
                                  │
                                  ▼
                        ┌───────────────────┐
                        │  CoordinatorAgent │ (Orchestrates State & Execution Graph)
                        └─────────┬─────────┘
                                  │
         ┌────────────────────────┼────────────────────────┐
         ▼                        ▼                        ▼
┌─────────────────┐      ┌─────────────────┐      ┌─────────────────┐
│    HashAgent    │      │  MetadataAgent  │      │    ModelAgent   │
├─────────────────┤      ├─────────────────┤      ├─────────────────┤
│ • MD5 Hash Tool │      │ • EXIF Tool     │      │ • SigLIP Tensor │
│ • SHA256 Tool   │      │ • Dimension Tool│      │   Inference Tool│
│                 │      │ • Steganography │      │ • Thresholding  │
└────────┬────────┘      └────────┬────────┘      └────────┬────────┘
         │                        │                        │
         └────────────────────────┼────────────────────────┘
                                  │
                                  ▼
                        ┌───────────────────┐
                        │    ReportAgent    │
                        ├───────────────────┤
                        │ • ISO Timestamp   │ ──► [ Final Enterprise Compliance Report ]
                        │ • JSON Formatter  │
                        └───────────────────┘
The 5 Specialized Autonomous Agents:
CoordinatorAgent (The Orchestrator): Controls the application lifecycle, splits incoming media payloads, kicks off parallel worker execution channels, and aggregates telemetry metrics.

HashAgent (Cryptographic Identity): Computes unique cryptographic payloads to ensure asset tracking and detect downstream asset tampering.

MetadataAgent (Structural Forensics): Extracts hidden headers, camera profiles, EXIF metadata tags, and checks for data-stripping anomalies.

ModelAgent (Neural Tensor Engine): Connects to the PyTorch SigLIP infrastructure via an MCP Server boundary to analyze deep layers of the image patch array.

ReportAgent (Compliance Synthesis): Compiles multi-agent outputs, adds standard ISO-8601 timestamps, and translates low-level matrices into human-readable corporate security actions.

🚀 Rubric Alignment & Key Concepts Met
   This project natively addresses the core evaluation criteria set by the Agents: Intensive Vibe Coding Course parameters:
   Agent / Multi-Agent System (ADK): Implemented directly in agent_main.py via asynchronous parallel coordination (asyncio.gather), running a real worker graph instead of text-generation approximations.
   MCP Server Configuration: The AI Model is isolated behind an interactive Model Context Protocol layout, treating the heavy neural network as an external computing capability called dynamically by the ModelAgent.
   Google Antigravity Integration: Demonstrated inside the workflow presentation, highlighting terminal trace logs tracking data execution across decoupled environments.
   Security Features: Implemented strict Cross-Origin Resource Sharing (CORS) security rings, zero-cloud metadata persistence layers, and absolute separation of local data fields.
   Deployability: The frontend is seamlessly separated and deployed on Netlify, while instructions for local hybrid-edge backend scaling are thoroughly documented below.
   
🛠️ Local Installation & Setup Guide
   Because loading deep computer vision libraries (PyTorch + Torchvision) and the 372MB SigLIP weights layer requires approximately 750MB+ of active RAM, this backend runs in a Hybrid Local-Edge Configuration. This ensures maximum computing speed and total data privacy.
   
Prerequisites
   Python 3.10 or Python 3.11 installed locally.A browser supporting HTML5/CSS3.
   
   Step 1: Install System DependenciesOpen your terminal inside the project directory and run the following command to download PyTorch (CPU variant) along with      necessary image processing layers:
   Bashpython -m pip install fastapi uvicorn pillow pydantic transformers torch torchvision --index-url https://download.pytorch.org/whl/cpu

   Step 2: Initialize the Multi-Agent System BackendTo bypass any Windows Application Control policies or file access constraints, execute the Uvicorn application    module directly through Python:
   Bashpython -m uvicorn agent_main:app --host 127.0.0.1 --port 8000 --reload

   Look for the success signature indicating the multi-agent system is live:
   Plaintext🌐 TRUTHIFY MAS (Multi-Agent System) ACTIVE
   ├─ ⏳ INITIALIZING: 5 Specialized Agents Booting...
   └─ ✅ SUCCESS: Coordinator Agent ready to accept MCP requests on http://127.0.0.1:8000

   Step 3: Run the User Interface
   
   Option A (Local): Open your web browser and go to [http://127.0.0.1:8000](http://127.0.0.1:8000) to interact with the local page served out of your static/ subdirectory.
   Option B (Cloud Frontend): Open your live Netlify deployment link ([https://truthifyai.netlify.app/](https://truthifyai.netlify.app/)) to interact with the cloud interface communicating with your active engine pipeline.
  
