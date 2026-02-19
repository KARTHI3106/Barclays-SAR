# AuditWatch -- SAR Narrative Generator

AI-powered Suspicious Activity Report generation engine with full regulatory audit trail, MCP tool servers, and multi-agent (A2A) architecture.

Built for Indian regulatory compliance (PMLA, 2002 / RBI Master Directions / FIU-IND).

---

## Architecture

```text
Input JSON --> DataParser --> RAG Engine --> LLM Orchestrator --> SAR Narrative
                  |              |               |                    |
                  v              v               v                    v
             Patterns      Templates      Ollama/Llama 3.1     5-Section STR
                  |              |               |                    |
                  +---------- Audit Logger (SQLite, 7-layer) --------+
```

### MCP Tool Servers (3 servers, 9 tools)

| Server                 | Tools                                                                | Description                                          |
| ---------------------- | -------------------------------------------------------------------- | ---------------------------------------------------- |
| `transaction_analyzer` | `analyze_transactions`, `calculate_baseline`, `classify_typology`    | Transaction parsing, pattern detection, risk scoring |
| `sar_template_engine`  | `retrieve_templates`, `generate_narrative`, `get_regulatory_context` | RAG retrieval, LLM narrative generation              |
| `audit_trail_manager`  | `log_decision`, `get_audit_trail`, `export_audit`                    | Immutable audit logging and export                   |

### A2A Multi-Agent Architecture (5 agents)

| Agent                 | Role                                              |
| --------------------- | ------------------------------------------------- |
| `CoordinatorAgent`    | Orchestrates the full pipeline, dispatches tasks  |
| `DataEnrichmentAgent` | Parses input, calculates stats, detects patterns  |
| `TypologyAgent`       | Classifies crime typology with confidence scoring |
| `NarrativeAgent`      | Generates SAR narrative via RAG + LLM             |
| `AuditAgent`          | Logs every step for regulatory traceability       |

---

## Quick Start

For detailed setup instructions, see **[SETUP.md](SETUP.md)** or **[how_to_run.md](how_to_run.md)**.

### Prerequisites

- Python 3.10+
- Ollama with `llama3.1:8b` model (for LLM generation)

### Setup

**Windows:**

```bash
cd project_files
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

**Linux/Mac:**

```bash
cd project_files
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Configure

1. Copy `.env.example` to `.env`
2. Edit `.env` with your settings (JWT secret, admin password)
3. Ensure Ollama is running: `ollama serve`
4. Pull the model: `ollama pull llama3.1:8b`

### Run

```bash
cd project_files
streamlit run src/ui/app.py
```

Open `http://localhost:8501` in your browser.

### Default Login Credentials

| Username      | Password         | Role          |
| ------------- | ---------------- | ------------- |
| `admin`       | `auditwatch2026` | Administrator |
| `analyst_01`  | `analyst123`     | Analyst       |
| `reviewer_01` | `reviewer123`    | Reviewer      |

---

## Demo Flow

1. **Login** as `admin`
2. **Input Case**: Select `case_003_50lakhs` from sample cases
3. **Generate**: Click "Generate SAR Narrative" -- watch the live pipeline animation
4. **Review**: Check the 5-section narrative, confidence breakdown, and compliance checker
5. **Export**: Download as PDF, JSON, CSV, or TXT
6. **Audit Trail**: View the 7-layer regulatory audit trail
7. **Architecture**: Explore MCP tool servers and A2A agent definitions

### Multi-Agent Mode

Toggle to "Multi-Agent (A2A)" in the sidebar to run the pipeline through the CoordinatorAgent, which dispatches tasks to 5 specialized agents with full message tracing.

---

## Project Structure

```text
project_files/
  config.yaml              # App config (model, DB, security -- no secrets)
  .env.example             # Environment variable template
  requirements.txt         # Python dependencies
  SETUP.bat / START.bat    # Windows automation scripts
  src/
    config.py              # Config loader with env var overrides
    main.py                # Pipeline orchestrator (direct + multi-agent)
    models/
      case_input.py        # Pydantic input models with validators
      sar_output.py        # SAR narrative and explainability models
      audit_trail.py       # Audit event model
    components/
      data_parser.py       # Transaction parsing, pattern detection, risk scoring
      rag_engine.py        # ChromaDB RAG for templates + regulatory data
      llm_orchestrator.py  # Ollama LLM integration with fallback
      audit_logger.py      # Dual-storage audit logger (SQLite + in-memory)
    agents/
      mcp_servers.py       # 3 MCP tool servers (9 tools total)
      a2a_agents.py        # 5 A2A agents with JSON-RPC messaging
    utils/
      auth.py              # JWT auth + RBAC (stdlib, no PyJWT)
      db_utils.py          # SQLite database manager (WAL mode)
      anonymization.py     # PII anonymization (deterministic hashing)
      pdf_generator.py     # ReportLab PDF generation
    prompts/
      system_prompt.txt    # LLM system prompt
      user_prompt_template.txt
    ui/
      app.py               # Streamlit app (6 pages, 1148 lines)
  data/
    sample_cases/          # 3 demo case JSON files
    templates/             # 5 SAR template narratives
    regulatory/            # Typology descriptions (PMLA/RBI)
  database/
    schema.sql             # SQLite schema (auto-created on first run)
  tests/
    test_comprehensive.py  # Core tests (20)
    test_qa_extended.py    # Extended QA tests (23)
```

---

## Security

- No hardcoded credentials (all via `.env`)
- JWT authentication with HS256 (stdlib `hmac` + `hashlib`, no external dependency)
- Role-based access control: `analyst` < `reviewer` < `admin`
- PII anonymization enabled by default
- SQLite with WAL journal mode for data integrity
- Input validation via Pydantic field validators

---

## Tech Stack

| Component  | Technology                             |
| ---------- | -------------------------------------- |
| LLM        | Ollama + Llama 3.1 8B (local, offline) |
| Vector DB  | ChromaDB                               |
| Database   | SQLite (stdlib)                        |
| Framework  | LangChain                              |
| UI         | Streamlit                              |
| Auth       | JWT (stdlib HS256)                     |
| PDF        | ReportLab                              |
| Validation | Pydantic v2                            |

---

## Troubleshooting

**Ollama not running:**

```bash
ollama serve
ollama pull llama3.1:8b
```

**ChromaDB permission errors:**
Delete the `chroma_db/` directory and restart -- it will be recreated.

**Import errors:**
Ensure you are running from the `project_files/` directory and the virtual environment is activated.

**Port 8501 in use:**

```bash
streamlit run src/ui/app.py --server.port 8502
```

---

## Testing

```bash
# Core tests (20 checks: bug fixes, auth, DB, MCP, A2A, config)
python tests/test_comprehensive.py

# Extended QA tests (23 checks: edge cases, integration, security)
python tests/test_qa_extended.py
```

All 43 tests pass with zero failures.

---

## Documentation

| Document                                             | Description                                                   |
| ---------------------------------------------------- | ------------------------------------------------------------- |
| [SETUP.md](SETUP.md)                                 | Complete setup guide (system reqs, model config, concurrency) |
| [how_to_run.md](how_to_run.md)                       | Step-by-step local setup and demo guide                       |
| [.env.example](.env.example)                         | Environment variable template                                 |

---


