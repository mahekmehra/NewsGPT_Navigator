# 🧠 NewsGPT Navigator (Victory Edition)

**AI-Native News Intelligence Engine** — An autonomous 10-agent intelligence platform that transforms raw news into structured, multimodal briefings. Orchestrated via LangGraph for a production-grade, hackathon-winning experience.

---

## 🚀 Victory Features

| Feature | Description |
|---------|-------------|
| **Multi-Agent Flow** | 10 specialized agents working in a perfect DAG (Fetch → Video → Delivery) |
| **Professional Audio** | gTTS-powered voice narration for every briefing (Concise & Clear) |
| **Dynamic Video** | Real-time YouTube scraping for analysis & thumbnails (No API keys needed) |
| **Entity Story Arcs** | NER + per-entity sentiment tracking across sessions |
| **Conflict & Emotion** | surfacing narrative contradictions and emotional register |
| **RAG Synthesis** | FAISS-powered cross-source reasoning for zero-duplication insights |
| **Clean API** | Streamlined FastAPI surface optimized for React frontend integration |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    FastAPI Backend                        │
│                   (api/main.py)                           │
├─────────────────────────────────────────────────────────┤
│              LangGraph Orchestrator                       │
│             (agents/orchestrator.py)                      │
├─────────────────────────────────────────────────────────┤
│                                                           │
│  Fetch → Entity/Sentiment → Angle → Analysis →           │
│  Compliance → Profile/Ranking → Conflict →                │
│  Emotion → Video → Delivery                               │
│                                                           │
├─────────────────────────────────────────────────────────┤
│  Core: LLM Router │ Embeddings │ Credibility │ Translator │
└─────────────────────────────────────────────────────────┘
```

### The 10 AI Agents

1. **Fetch**: Multi-source ingestion + Quality/Credibility scoring.
2. **Entity Sentiment**: NER + Sentiment tagging + Story Arc trends.
3. **Angle Decomposition**: Narrative clustering + FAISS index builds.
4. **Analysis**: RAG-based synthesis with structured metadata.
5. **Compliance**: Sensationalism & bias filtering.
6. **Profile Ranking**: Persona-specific content tailoring.
7. **Conflict**: Surfacing factual and interpretive contradictions.
8. **Emotional Calibration**: Crisis/Opportunity detection & Tone guidance.
9. **Video**: Dynamic YouTube scraping for analysis & thumbnails.
10. **Delivery**: Final persona briefing + Translation + Audio generation.

---

## 📁 Storage & Assets

- `data/audio_output/`: Stores generated MP3 voice narrations.
- `data/video_output/`: Stores video-related metadata.
- `data/knowledge_store/`: Persistent session memory for Story Arcs.
- `core/`: High-performance utilities (LLM Routing, Vector Search).

---

## ⚡ Quick Start

### 1. Setup
```bash
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```

### 2. Keys
Edit `.env` with `GROQ_API_KEY` and `NEWS_API_KEY`.

### 3. Run
```bash
uvicorn api.main:app --reload
```

---

## 📡 Essential Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/analyze` | Run full 10-agent pipeline |
| `GET` | `/audio/{file}`| Serve voice narration MP3s |
| `GET` | `/health` | System status & Agent readiness |
| `GET` | `/languages` | Supported translation codes |
| `GET` | `/personas` | Pre-configured intelligence presets |

### Example Request

```bash
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "Union Budget 2025",
    "persona": "Investor",
    "language": "en"
  }'
```

---

## 🎯 Demo Flow

1. **Topic**: Enter "Union Budget 2025" or "AI Regulation"
2. **Persona Switch**: Compare **Investor** view vs **Student** view
3. **Key Outputs**: Summary → Angles → Timeline → Prediction → Follow-up Questions
4. **Multimedia**: Audio narration + YouTube links
5. **Intelligence**: Conflict detection + Emotional calibration

---

## 🛠️ Tech Stack

- **Orchestration**: LangGraph (StateGraph DAG)
- **LLM**: Groq (Llama 3.1 8B / Llama 3.3 70B with smart routing)
- **Embeddings**: Sentence-Transformers + FAISS
- **Backend**: FastAPI + Pydantic
- **Audio**: gTTS
- **Translation**: deep-translator (Google Translate)
- **News**: NewsAPI

---

## 📄 License

MIT
