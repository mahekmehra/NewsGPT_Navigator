# 🧠 NewsGPT Navigator

**AI-Powered News Intelligence Engine** — A 10-agent autonomous platform that transforms raw news into structured, persona-tailored, multilingual intelligence briefings. Built with LangGraph, Groq LLMs, and FAISS vector search.

🚀 **Deployed on Render**: [https://newsgpt-navigator.onrender.com](https://newsgpt-navigator.onrender.com)

---


## ✨ Key Features

| Feature | Description |
|---------|-------------|
| **10-Agent Pipeline** | Specialized agents in a LangGraph DAG — from ingestion to delivery |
| **Persona Briefings** | LLM-generated briefs tailored per persona (Investor, CFO, Student, etc.) |
| **Audio Narration** | gTTS-powered voice briefings with multilingual support |
| **YouTube Integration** | Dynamic video scraping — titles, links, thumbnails (no API key needed) |
| **Entity Story Arcs** | NER + per-entity sentiment tracking across sessions |
| **Conflict Detection** | Surfaces factual, interpretive, and predictive contradictions |
| **Emotional Calibration** | Crisis/Opportunity/Uncertainty register with tone guidance |
| **RAG Synthesis** | FAISS-powered cross-source reasoning for zero-duplication insights |
| **Bias & Compliance** | Real-time sensationalism, political skew, and source credibility checks |
| **Multilingual** | Supports English + 7 Indian languages (Hindi, Punjabi, Tamil, Bengali, Telugu, Kannada, Marathi) |

---


### 🏗️ Architecture Document

#### **The Intelligence Core (LangGraph DAG)**
NewsGPT Navigator operates as an autonomous newsroom. It is built on a **StateGraph** where 10 specialized agents communicate via a shared `PipelineState`.

1.  **Shared State Architecture**: Every agent reads the "Current Context" and contributes its findings. This prevents the "hallucination" common in single-agent systems.
2.  **The Assembly Line**:
    *   **Perception**: `Fetch` (Ingestion) & `Entity Sentiment` (NER).
    *   **Strategic Reasoning**: `Angle` (Narrative clustering) & `Analysis` (RAG Synthesis).
    *   **Compliance & Trust**: `Compliance` (Bias scoring) & `Conflict` (Fact-checking).
    *   **Personalization**: `Profile Ranking` & `Emotion` (Tone calibration).
    *   **Multimodal Output**: `Video` (YouTube scraping) & `Delivery` (Translation & Audio).

#### **Resiliency & Error Handling**
*   **Recursive Retries**: Automated fallback nodes (e.g., `retry_fetch`) handle API failures.
*   **Compliance Loops**: If a briefing fails bias thresholds, it is automatically routed back for re-analysis.
*   **Safe Parsing**: Resilient JSON parsing ensures the system remains upright even with malformed LLM outputs.

---

### 📈 Impact Model (Track 8: AI-Native News)

Business news in 2026 demands **Time-to-Value**. NewsGPT Navigator solves the "2005 Problem" of static, generic delivery by providing persona-optimized intelligence in seconds.

#### **Quantified Business Impact**
Comparison based on a **Financial Analyst** synthesizing 10 global articles into a bespoke brief.

| Metric | Manual Analyst | NewsGPT Navigator | Efficiency Gain |
|--------|----------------|--------------------|-----------------|
| **Time-to-Value** | 180 Minutes | 45 Seconds | **~99.5% Faster** |
| **Operational Cost** | $150 (Manual) | ~$0.05 (Tokens) | **~3,000x Cost Save** |
| **Personalization** | One-to-Many | One-to-One | **N/A (Scalable)** |
| **Objectivity** | Subjective | Auditable Bias score | **Quality Guardrails** |

---

### The 10 AI Agents

| # | Agent | Role |
|---|-------|------|
| 1 | **Fetch** | Multi-source ingestion + quality/credibility scoring |
| 2 | **Entity Sentiment** | NER + sentiment tagging + story arc trends |
| 3 | **Angle Decomposition** | Narrative clustering + per-angle FAISS indexes |
| 4 | **Analysis** | RAG-based synthesis with structured metadata |
| 5 | **Compliance** | Sensationalism & bias filtering (score threshold) |
| 6 | **Profile Ranking** | Persona-specific content tailoring & ranking |
| 7 | **Conflict** | Factual, interpretive, and predictive conflict detection |
| 8 | **Emotional Calibration** | Crisis/Opportunity detection & tone guidance |
| 9 | **Video** | Dynamic YouTube scraping for links & thumbnails |
| 10 | **Delivery** | Final persona brief + translation + audio generation |

---

## 📁 Project Structure

```
news-gpt/
├── agents/                 # 10 LangGraph agent nodes + orchestrator
│   ├── orchestrator.py     # DAG builder & pipeline entry point
│   ├── state.py            # Shared TypedDict state schema
│   ├── fetch_agent.py
│   ├── entity_sentiment_agent.py
│   ├── angle_agent.py
│   ├── analysis_agent.py
│   ├── compliance_agent.py
│   ├── profile_ranking_agent.py
│   ├── conflict_agent.py
│   ├── emotional_agent.py
│   ├── video_agent.py
│   └── delivery_agent.py
├── api/                    # FastAPI backend
│   ├── main.py             # Endpoints & static file serving
│   └── schemas.py          # Pydantic request/response models
├── core/                   # Shared utilities
│   ├── config.py           # Settings from .env
│   ├── llm_router.py       # Smart Groq model routing
│   ├── embeddings.py       # Sentence-transformers + FAISS
│   ├── credibility.py      # Source credibility checker
│   ├── news_fetcher.py     # NewsAPI client + fallback
│   ├── safe_json.py        # Resilient LLM JSON parser
│   └── translator.py       # Multi-language translation
├── data/                   # Runtime data & static assets
│   ├── credible_sources.json
│   ├── sample_articles.json
│   ├── audio_output/       # Generated MP3 narrations
│   ├── video_output/       # Video metadata
│   └── knowledge_store/    # Session memory for story arcs
├── web/                    # React + Vite frontend
│   ├── src/
│   └── dist/               # Production build (gitignored)
├── tests/                  # Pytest test suite
├── requirements.txt        # Python dependencies
├── .env.example            # Environment variable template
└── README.md
```

---

## ⚡ Quick Start

### 1. Clone & Setup

```bash
git clone https://github.com/your-username/news-gpt.git
cd news-gpt

# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (macOS/Linux)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure API Keys

```bash
cp .env.example .env
```

Edit `.env` and add your keys:
- **`GROQ_API_KEY`** — Free at [console.groq.com](https://console.groq.com)
- **`NEWS_API_KEY`** — Free at [newsapi.org](https://newsapi.org)

### 3. Run the Backend

```bash
uvicorn api.main:app --reload
```

The API will be available at `http://localhost:8000`.

### 4. Run the Frontend (Development)

```bash
cd web
npm install
npm run dev
```

Frontend runs at `http://localhost:5173` with API proxy to the backend.

### 5. Build Frontend for Production

```bash
cd web
npm run build
```

The built files are served automatically by the backend at `/`.

---

## 📡 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/analyze` | Run the full 10-agent pipeline |
| `GET` | `/audio/{file}` | Serve generated audio narrations |
| `GET` | `/video/{file}` | Serve video files |
| `GET` | `/health` | System status & agent readiness |
| `GET` | `/languages` | Supported translation languages |
| `GET` | `/personas` | Available persona presets |

### Example Request

```bash
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "AI Regulation 2026",
    "persona": "Investor",
    "language": "en"
  }'
```

---

## 🧪 Running Tests

```bash
python -m pytest tests/ -v
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| **Orchestration** | LangGraph (StateGraph DAG) |
| **LLM** | Groq (Llama 3.1 8B / Llama 3.3 70B with smart routing) |
| **Embeddings** | Sentence-Transformers + FAISS |
| **Backend** | FastAPI + Pydantic |
| **Frontend** | React + TypeScript + Vite + Tailwind CSS |
| **Audio** | gTTS (Google Text-to-Speech) |
| **Translation** | deep-translator (Google Translate) |
| **News** | NewsAPI |

**Build by Mahek Mehra**
