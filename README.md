# 🧠 NewsGPT Navigator

**Autonomous Multi-Agent News Intelligence Platform**

11 AI agents + Story Arc Tracker | LangGraph DAG orchestration | Groq-powered LLMs | React dashboard

---

## Architecture

```
Topic → Fetch → Entity/Sentiment → Angle Decomposition → Analysis (RAG)
                      ↓                      ↓
              Story Arc Tracker      Conflict Detection
                                           ↓
         Profile/Ranking → Compliance → Emotional Calibration → Delivery
                                           ↓
                                    Knowledge Diff → Video (Multilingual TTS)
```

### 11 Agent Pipeline

| # | Agent | Role | Model |
|---|-------|------|-------|
| 1 | **Fetch** | Multi-source article retrieval + credibility scoring | NewsAPI + scoring engine |
| 2 | **Entity/Sentiment** | Named entity extraction + sentiment analysis | 8B |
| 3 | **Angle Decomposition** | Cluster articles into narrative angles | 8B |
| 4 | **Analysis** | RAG-powered summary, timeline, prediction | 70B |
| 5 | **Compliance** | Bias detection, content guardrails, SEBI flag | 70B |
| 6 | **Profile/Ranking** | User persona profiling + article ranking | 8B |
| 7 | **Conflict Detection** | Cross-source factual/narrative conflict flagging | 70B |
| 8 | **Emotional Calibration** | Tone + register calibration for delivery | 8B |
| 9 | **Delivery** | Persona-formatted, multilingual briefing | 8B |
| 10 | **Knowledge Diff** | Session-aware knowledge state tracking | 8B |
| 11 | **Video** | Multilingual TTS video generation (< 60s) | 8B + gTTS + MoviePy |

### Unique Features

- **Story Arc Tracker** — Temporal sentiment trends showing how entity sentiment evolves across sessions (e.g. "Adani: negative → neutral over 5 weeks")
- **Custom Personas** — Free-text persona input (e.g. "startup founder", "journalist") dynamically profiled by LLM
- **Multilingual Video** — Auto-generated news videos in Hindi, Tamil, Telugu, Bengali with language-specific jargon cleaning
- **safe_json_parse** — 5-stage resilient JSON parser across all agents; pipeline never crashes on malformed LLM output
- **Stress-Test Endpoint** — `/stress-test` validates all agents, pipeline compilation, and API keys before a demo

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| **Orchestration** | LangGraph (StateGraph DAG) |
| **LLM** | Groq API (Llama 3.3 70B + Llama 3.1 8B) |
| **Backend** | FastAPI + Pydantic |
| **Frontend** | React + Vite |
| **Vector Store** | FAISS (sentence-transformers) |
| **Video** | gTTS + MoviePy + Pillow |
| **Testing** | pytest |

---

## Quick Start

```bash
# 1. Clone & install
git clone <repo-url> && cd news-gpt
pip install -r requirements.txt
cd frontend && npm install && cd ..

# 2. Configure
cp .env.example .env
# Add GROQ_API_KEY and NEWS_API_KEY

# 3. Run
uvicorn api.main:app --reload       # Backend → :8000
cd frontend && npm run dev           # Frontend → :5173

# 4. Pre-demo smoke test
curl http://localhost:8000/stress-test
```

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/analyze` | Run 11-agent pipeline (accepts `topic`, `persona`, `custom_persona`, `language`) |
| `GET` | `/health` | Agent health check |
| `GET` | `/languages` | Supported languages |
| `GET` | `/personas` | Available personas + custom examples |
| `GET` | `/sessions` | List analysis sessions |
| `GET` | `/audit/{id}` | Session audit trail |
| `GET` | `/stress-test` | Pre-demo smoke test |

---

## Project Structure

```
news-gpt/
├── agents/
│   ├── orchestrator.py          # LangGraph DAG (11 nodes + 4 control)
│   ├── state.py                 # PipelineState TypedDict
│   ├── fetch_agent.py           # Article retrieval
│   ├── entity_sentiment_agent.py # Entity extraction + Story Arc
│   ├── angle_agent.py           # Angle clustering
│   ├── analysis_agent.py        # RAG summary + timeline
│   ├── compliance_agent.py      # Bias/compliance checks
│   ├── profile_ranking_agent.py # Persona profiling + custom persona
│   ├── conflict_agent.py        # Conflict detection
│   ├── emotional_agent.py       # Tone calibration
│   ├── delivery_agent.py        # Persona-formatted briefing
│   ├── knowledge_diff_agent.py  # Knowledge state tracking
│   └── video_agent.py           # Multilingual video (Hi/Ta/Te/Bn)
├── core/
│   ├── config.py                # Settings & model routing
│   ├── llm_router.py            # Groq API + model selection
│   ├── safe_json.py             # 5-stage resilient JSON parser
│   ├── credibility.py           # Source credibility scoring
│   └── embeddings.py            # FAISS vector store
├── api/
│   ├── main.py                  # FastAPI app + /stress-test
│   └── schemas.py               # Pydantic models
├── data/
│   ├── jargon_map.json          # Hindi/Tamil/Telugu/Bengali jargon
│   ├── persona_presets.json     # 8 persona presets
│   └── credible_sources.json    # Source credibility DB
├── frontend/src/
│   ├── App.jsx                  # Main app with 12 pages
│   ├── components/
│   │   ├── Navbar.jsx           # Sidebar navigation
│   │   └── TopicInput.jsx       # Topic + custom persona input
│   └── pages/
│       ├── StoryArc.jsx         # Temporal sentiment tracker
│       ├── EntityMap.jsx        # Entity/sentiment visualization
│       ├── VideoPlayer.jsx      # Video player
│       └── ...                  # 9 more pages
├── tests/
│   ├── test_state.py            # State schema tests
│   ├── test_graph.py            # Pipeline compilation tests
│   ├── test_api.py              # API endpoint tests
│   └── test_surprise.py         # Surprise scenario resilience tests
└── requirements.txt
```

---

## Testing

```bash
# Run all tests
python -m pytest tests/ -v

# Run only surprise/resilience tests
python -m pytest tests/test_surprise.py -v

# Quick import smoke test
python -c "from core.safe_json import safe_json_parse; print(safe_json_parse('not json', {'ok': True}))"
```

---

## Supported Languages

| Code | Language | Analysis | Video TTS | Jargon Map |
|------|----------|----------|-----------|------------|
| `en` | English | ✅ (Primary) | N/A | N/A |
| `hi` | Hindi | ✅ | ✅ | ✅ (50+ terms) |
| `ta` | Tamil | ✅ | ✅ | ✅ (20 terms) |
| `te` | Telugu | ✅ | ✅ | ✅ (20 terms) |
| `bn` | Bengali | ✅ | ✅ | ✅ (20 terms) |
| `kn` | Kannada | ✅ | — | — |
| `mr` | Marathi | ✅ | — | — |
| `pa` | Punjabi | ✅ | — | — |
