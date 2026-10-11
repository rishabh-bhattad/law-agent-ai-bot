# Live Case-Law Briefing Bot ⚖️

An autonomous, multi-stage legal research agent and case brief generator. It translates natural-language legal questions into targeted case-law queries against the **CourtListener REST API**, executes a 5-stage state-machine pipeline to extract issues and synthesize holdings, audits for hallucinations, and serves structured case briefs to a React frontend.

---

## 🌟 Key Features

- **Multi-Stage Workflow Pipeline:** Decoupled 5-stage state machine (`Context`, `Runner`, `Steps`, `Registry`, `Pipeline`):
  1. **Query Optimization:** LLM rewrites conversational user questions into quoted case names, boolean operators, and jurisdiction filters (`scotus`).
  2. **Case Search:** Fetches precedential written opinions via CourtListener REST API with exponential backoff retries.
  3. **Issue Extraction:** Unpacks primary constitutional questions, material facts, and court reasoning into a structured `LegalAnalysis` schema.
  4. **Brief Drafting:** Synthesizes an authoritative legal brief with explicit constitutional amendments, clauses, and holding rules.
  5. **QA & Anti-Hallucination Review:** Audits the draft brief against raw court text, eliminates hallucinated facts, and verifies citations.
- **Enterprise Resiliency:** External API calls to CourtListener and Google Gemini are protected by `tenacity` exponential backoff retries.
- **Security Guardrails:** Pre-LLM regex detection blocks prompt injection attacks (`400 Bad Request`) before invoking any model.
- **OpenTelemetry Observability:** Distributed tracing auto-instruments incoming FastAPI requests and outbound HTTP calls.
- **Docker Containerization:** Full multi-container orchestration (`docker-compose.yml`) packaging the Python 3.12 backend and Nginx-served React frontend for consistent local dev and cloud deployment.
- **Automated LLM-as-a-Judge Evaluation:** Automated benchmark suite (`eval/run_eval.py`) scores output on *Factual Accuracy* (5.0/5.0), *Holding Correctness* (5.0/5.0), and *Citation Relevance* (4.5/5.0).
- **Modern Web Interface:** Full React + Vite + Tailwind CSS frontend with live query status and detailed brief cards.

---

## 📁 Repository Structure

```
law-agent-ai-bot/
├── app/                         # FastAPI backend application
│   ├── api/                     # REST API routers & dependency injection
│   │   ├── deps.py              # Injected service providers (CourtListener, LLM, Pipeline)
│   │   └── generate.py          # POST /api/v1/generate endpoint
│   ├── core/                    # Core infrastructure & configuration
│   │   ├── config.py            # Pydantic Settings loaded from .env
│   │   ├── guardrails.py        # Regex prompt-injection scanner
│   │   └── telemetry.py         # OpenTelemetry distributed tracing setup
│   ├── integrations/            # External service integrations
│   │   ├── courtlistener.py     # CourtListener v4 REST API client with retry logic
│   │   └── llm/                 # LLM provider protocol & Gemini SDK implementation
│   ├── prompts/                 # Prompt templates and universal rules
│   │   ├── rules/               # Global anti-hallucination markdown rules
│   │   └── templates/           # Step-specific templates (optimize, analyze, draft, qa)
│   ├── schemas/                 # Pydantic models (CaseBrief, LegalAnalysis, SearchPlan)
│   ├── workflow/                # Domain-driven multi-stage workflow engine
│   │   ├── context.py           # WorkflowContext shared memory container
│   │   ├── runner.py            # Sequential step execution runner
│   │   ├── briefing_steps.py    # The 5 workflow execution nodes
│   │   ├── registry.py          # Workflow step recipe assembler
│   │   └── pipeline.py          # Master orchestrator & general contractor
│   └── main.py                  # FastAPI entry point, CORS, and route registration
├── frontend/                    # React + TypeScript + Vite frontend
│   ├── src/                     # UI components, types, and API client
│   ├── Dockerfile               # Multi-stage Nginx container build
│   └── package.json             # Frontend dependencies
├── eval/                        # Automated evaluation suite
│   └── run_eval.py              # LLM-as-a-judge benchmarking script
├── tests/                       # Automated test suite
│   ├── mocks.py                 # Fake LLM and CourtListener client test doubles
│   └── test_workflow.py         # Pytest async pipeline and guardrail unit tests
├── docs/                        # Architecture guides and Progressive Build blueprints
│   └── architecture_walkthrough.md # Deep-dive into DI, state machines & 17 core concepts
├── Dockerfile                   # Backend Python 3.12 slim container
├── docker-compose.yml           # Multi-container orchestration (Backend + Frontend)
└── requirements.txt             # Python production dependencies
```

---

## 🚀 Quick Start & How to Run

### 1. Prerequisites

- **Python 3.11+** or **Python 3.12**
- **Node.js 18+** & npm (for local frontend dev)
- **Docker & Docker Compose** (optional, for containerized run)
- **API Keys:**
  - Google Gemini API Key ([Google AI Studio](https://aistudio.google.com/))
  - CourtListener API Token ([CourtListener API](https://www.courtlistener.com/help/api/rest/v4/))

---

### 2. Environment Setup

Create a `.env` file in the root directory:

```env
# Project Settings
PROJECT_NAME="Live Case-Law Briefing Bot"
DEBUG=False

# LLM Provider ('gemini')
LLM_PROVIDER=gemini
GEMINI_API_KEY=your_gemini_api_key_here

# CourtListener REST API
COURTLISTENER_API_KEY=your_courtlistener_token_here
COURTLISTENER_BASE_URL=https://www.courtlistener.com/api/rest/v4

# Optional/Fallback Provider Keys
OPENAI_API_KEY=""
ANTHROPIC_API_KEY=""
```

---

### 3. Option A: Run with Docker Compose (Recommended)

To start both the backend API and frontend with a single command:

```bash
docker compose up --build
```

- **Frontend App:** http://localhost:3000
- **Backend API & Swagger Docs:** http://localhost:8000/docs
- **Health Check:** http://localhost:8000/health

---

### 4. Option B: Run Locally (Development Mode)

#### A. Run the Backend API

1. Create and activate a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate    # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Start the FastAPI development server:
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```
   Interactive Swagger documentation is available at **http://127.0.0.1:8000/docs**.

#### B. Run the Frontend

1. Navigate to the `frontend` directory:
   ```bash
   cd frontend
   ```

2. Install dependencies and start the Vite dev server:
   ```bash
   npm install
   npm run dev
   ```

3. Open **http://localhost:5173** in your browser.

---

## 🧪 Testing & Evaluation

### 1. Run Unit Tests (Fast & Free)
Runs the test suite using in-memory mock clients (`tests/mocks.py`) to verify the state machine and prompt-injection guardrails without incurring API costs:

```bash
pytest tests/test_workflow.py -v
```

### 2. Run the LLM-as-a-Judge Evaluation Suite
Runs live CourtListener retrieval and Gemini generation against landmark legal benchmarks (*Roe v. Wade*, *Miranda v. Arizona*), grading accuracy, holdings, and citations on a 1–5 scale:

```bash
python -m eval.run_eval
```

---

Built with ❤️ by Rish