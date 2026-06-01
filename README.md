# 🧠 AI-Powered Product Strategy Assistant

A multi-agent AI system that transforms raw business data into actionable product strategy insights using a LangGraph-powered agent pipeline.

---

## 📐 Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                    STREAMLIT FRONTEND (app.py)                  │
│   [Upload Files] [Run Analysis] [Chat] [Download PDF]           │
└──────────────────────────┬──────────────────────────────────────┘
                           │ HTTP (REST API)
┌──────────────────────────▼──────────────────────────────────────┐
│                    FASTAPI BACKEND (main.py)                     │
│  /upload  /analyze  /chat  /report/pdf  /status  /documents     │
└─────┬────────────────────┬─────────────────────────────────────┘
      │                    │
      ▼                    ▼
┌──────────┐    ┌──────────────────────────────────────────────┐
│ ChromaDB │    │         LANGGRAPH ORCHESTRATOR               │
│ Vector   │    │  (orchestrator.py — StateGraph pipeline)     │
│ Store    │    │                                              │
│          │    │  ┌──────────────────────────────────────┐   │
│ Semantic │    │  │  Agent 1: Customer Feedback Agent    │   │
│ Search   │    │  │  → Pain points, sentiment, requests  │   │
│          │    │  └─────────────┬────────────────────────┘   │
│          │    │                ▼                             │
│          │    │  ┌──────────────────────────────────────┐   │
│          │    │  │  Agent 2: Market Research Agent      │   │
│          │    │  │  → Trends, segments, opportunities   │   │
│          │    │  └─────────────┬────────────────────────┘   │
│          │    │                ▼                             │
│          │    │  ┌──────────────────────────────────────┐   │
│          │    │  │  Agent 3: Competitor Analysis Agent  │   │
│          │    │  │  → Gaps, threats, differentiation    │   │
│          │    │  └─────────────┬────────────────────────┘   │
│          │    │                ▼                             │
│          │    │  ┌──────────────────────────────────────┐   │
│          │    │  │  Agent 4: SWOT Analysis Agent        │   │
│          │    │  │  → Strengths, Weaknesses, O/T        │   │
│          │    │  └─────────────┬────────────────────────┘   │
│          │    │                ▼                             │
│          │    │  ┌──────────────────────────────────────┐   │
│          │    │  │  Agent 5: Feature Prioritization     │   │
│          │    │  │  → RICE scoring, roadmap             │   │
│          │    │  └─────────────┬────────────────────────┘   │
│          │    │                ▼                             │
│          │    │  ┌──────────────────────────────────────┐   │
│          │    │  │  Agent 6: Executive Report Agent     │   │
│          │    │  │  → Summary, strategy, KPIs           │   │
│          │    │  └─────────────┬────────────────────────┘   │
│          │    └────────────────┼─────────────────────────────┘
└──────────┘                     ▼
                         ┌──────────────┐
                         │  OpenAI API  │
                         │  (GPT-4o     │
                         │   Mini)      │
                         └──────────────┘
```

---

## 📁 Project Structure

```
product_strategy_assistant/
├── app.py                        # Streamlit frontend
├── main.py                       # FastAPI backend
├── orchestrator.py               # LangGraph multi-agent pipeline
├── requirements.txt
├── .env.example
├── start.sh                      # One-command startup
│
├── agents/
│   ├── customer_feedback_agent.py
│   ├── market_research_agent.py
│   ├── competitor_analysis_agent.py
│   ├── swot_agent.py
│   ├── feature_prioritization_agent.py
│   └── executive_report_agent.py
│
├── utils/
│   ├── llm_client.py             # OpenAI client config
│   ├── vector_store.py           # ChromaDB operations
│   ├── document_parser.py        # CSV/PDF/TXT/JSON parser
│   └── pdf_generator.py          # fpdf2 PDF generation
│
├── data/
│   └── sample_sales.csv          # ← Place your CSV here
│
├── reports/                      # Generated PDFs saved here
└── chroma_db/                    # ChromaDB persistent storage
```

---

## ⚙️ Setup & Installation

### 1. Clone / navigate to project
```bash
cd product_strategy_assistant
```

### 2. Create virtual environment
```bash
python -m venv venv
source venv/bin/activate        # Linux/Mac
venv\Scripts\activate           # Windows
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure environment
```bash
cp .env.example .env
```

Edit `.env`:
```env
OPENAI_API_KEY=your_actual_api_key_here
OPENAI_BASE_URL=https://keygateway.arshnivlabs.com/v1
OPENAI_USERNAME=Learner001
MODEL_NAME=gpt-4o-mini
MAX_TOKENS=500
```

### 5. Place your data
```
data/sample_sales.csv    ← your sales CSV goes here
```

---

## 🚀 Running the Application

### Option A — One command (recommended)
```bash
chmod +x start.sh
./start.sh
```

### Option B — Manual (two terminals)

**Terminal 1 — Backend:**
```bash
uvicorn main:app --reload --port 8000
```

**Terminal 2 — Frontend:**
```bash
streamlit run app.py
```

### Access
| Service | URL |
|---------|-----|
| Streamlit UI | http://localhost:8501 |
| FastAPI Backend | http://localhost:8000 |
| API Swagger Docs | http://localhost:8000/docs |

---

## 🎯 Usage Guide

1. **Upload Documents** — Upload CSV, PDF, TXT, or JSON files (or auto-load the sample CSV)
2. **Run Analysis** — Click "Run Full Analysis" to trigger all 6 agents
3. **View Results** — Navigate to "Analysis Results" tab for full breakdown
4. **Chat** — Ask natural language questions about your data
5. **Download PDF** — Click "Generate & Download PDF Report" for the executive report

---

## 🤖 Agent Responsibilities

| Agent | Input | Output |
|-------|-------|--------|
| Customer Feedback | Customer data from ChromaDB | Pain points, sentiment, feature requests |
| Market Research | Market/sales data from ChromaDB | Trends, segments, growth opportunities |
| Competitor Analysis | Competitor data + customer insights | Competitive gaps, threats, differentiation |
| SWOT Analysis | All previous agent outputs | Structured SWOT matrix + implications |
| Feature Prioritization | Customer + SWOT + market insights | RICE-scored feature list + roadmap |
| Executive Report | All agent outputs | Executive summary + strategic action plan |

---

## 📄 Output Formats

- **In-app display** — Expandable sections per agent in Streamlit
- **Downloadable PDF** — Full formatted executive report
- **Chat responses** — Context-aware Q&A

---

## 🔧 Technology Stack

| Component | Technology |
|-----------|-----------|
| LLM | GPT-4o Mini (via custom endpoint) |
| Agent Framework | LangGraph 0.1 + LangChain 0.2 |
| Vector Database | ChromaDB (local persistent) |
| Backend API | FastAPI 0.111 |
| Frontend | Streamlit 1.35 |
| PDF Generation | fpdf2 2.7 |
| Document Parsing | pandas, pdfplumber |

---

## 🌐 Deployment (Render / Railway)

### Environment variables to set:
```
OPENAI_API_KEY=...
OPENAI_BASE_URL=https://keygateway.arshnivlabs.com/v1
OPENAI_USERNAME=Learner001
MODEL_NAME=gpt-4o-mini
MAX_TOKENS=500
API_BASE_URL=https://your-backend-url.onrender.com
```

### Start commands:
- **Backend:** `uvicorn main:app --host 0.0.0.0 --port $PORT`
- **Frontend:** `streamlit run app.py --server.port $PORT --server.address 0.0.0.0`
