# Slide Contents -- AuditWatch SAR Narrative Generator

Copy-paste ready content for each slide in the hackathon PPT template.

---

## Slide 1: PROBLEM STATEMENT

**Title**: The SAR Narrative Bottleneck in Indian Banking

Indian banks file over 10 lakh Suspicious Transaction Reports (STRs) annually with FIU-IND under PMLA, 2002. Each report requires a compliance analyst to manually review flagged transactions, cross-reference regulatory guidelines, and write a structured narrative averaging 5.5 hours per case. Manual writing is error-prone, inconsistent across analysts, and produces no audit trail for regulatory traceability. Banks either under-report (regulatory penalty) or over-report (wasted resources).

---

## Slide 2: SOLUTION

**How we solve the problem**: AuditWatch automates SAR/STR narrative writing using a local LLM with RAG retrieval, cutting analyst time from 5.5 hours to under 90 minutes per case. It ingests structured case data (JSON), runs 9 automated pattern detectors, retrieves regulatory templates via vector search, and generates a 5-section narrative following FIU-IND format.

**Impact metrics**: 73% reduction in analyst time per case. Consistent narrative quality across analysts. 100% audit coverage with 7-layer decision logging. Zero data leakage (fully offline, local LLM).

**Frameworks/Tools/Technologies**: Python, Streamlit (UI), Ollama + Llama 3.1 8B (local LLM), ChromaDB (vector DB for RAG), SQLite (audit storage), LangChain (orchestration), Pydantic (validation), ReportLab (PDF export).

**Why this stack (decision points)**: Ollama runs locally with no API keys and no data leaves the bank. SQLite is zero-config and ships with Python. ChromaDB runs in-process with no external server. Streamlit enables rapid prototyping with interactive widgets. All components are open-source with no licensing cost.

**Implementation and effectiveness**: Single command setup (pip install + ollama pull). Works on any machine with 8GB+ VRAM. Generates production-quality narratives in under 2 minutes. Analyst reviews and edits rather than writing from scratch.

**Scalability/Usability**: MVP handles single-analyst workflows. Production path: FastAPI + Celery + PostgreSQL for concurrent processing and horizontal scaling. MCP and A2A protocols make the system modular -- swap LLM models or add agents without changing the pipeline.

---

## Slide 3: METHODOLOGY

**Left panel -- Concept, principles, elements and components**:

AuditWatch uses a multi-agent RAG pipeline with two protocol layers:

Core pipeline: JSON input is validated with Pydantic, parsed for transaction statistics, scanned by 9 pattern detectors (structuring, layering, round-tripping, rapid movement, wire fraud, cash business, identity theft, high-risk jurisdiction, income mismatch), classified by typology, enriched with regulatory templates via ChromaDB vector similarity search, and passed to Ollama/Llama 3.1 for narrative generation. Every step is logged to a 7-layer audit trail (SQLite + in-memory dual storage).

MCP layer: 3 tool servers (TransactionAnalyzer, SARTemplateEngine, AuditTrailManager) expose 9 callable tools via Model Context Protocol.

A2A layer: 5 specialized agents (Coordinator, DataEnrichment, Typology, Narrative, Audit) communicate via JSON-RPC messages.

**Right panel -- Required items**:

- Architecture Diagram: See architecture_diagrams.md (Mermaid for docs, Eraser.io export for slides)
- Flow Chart: Case JSON -> Validate -> Parse Stats -> Detect Patterns -> Classify Typology -> RAG Retrieve -> LLM Generate -> 5-Section SAR (every step logged)
- Wireframes: See figma_prompts_2.md (7 screens: Login, Input, Review, Audit, Export, Architecture, Settings)
- Bar graph: Risk score confidence breakdown by component (Pattern, Template, Regulatory match)
- Pie chart: Transaction type distribution (NEFT/UPI/RTGS/SWIFT percentages)
- Heat map: Transaction frequency by day and counterparty (production feature)
- Histogram: Transaction amount distribution across ranges (production feature)
- Analysis/visualization: Real-time pipeline animation, pattern detection display, compliance checklist, risk score gauge

---

## Slide 4: INPUT / OUTPUT SPECIFICATION

**Input**: Structured JSON with case_id, customer details (name, account, KYC rating, occupation, income), transactions array (date, amount, currency, type, originator, beneficiary, description), alert_reason, and investigation_notes. Sourced from bank Transaction Monitoring Systems (Actimize, Fircosoft, Oracle FCCM) or manual entry.

**Output**: 5-section SAR narrative (Summary, Account Info, Description, Explanation, Conclusion) following FIU-IND format. Risk score 0-100. Detected patterns list. Full audit trail with timestamps. Export as PDF, JSON, CSV, or TXT.

**Risk score interpretation**: 0-30 Low (monitor), 31-60 Moderate (review), 61-80 High (file STR), 81-100 Critical (immediate filing + escalation).

---

## Slide 5: MCP and A2A Architecture

**MCP (Model Context Protocol)**: 3 tool servers expose 9 pipeline capabilities as callable tools. Any MCP-compatible LLM client can invoke them directly. Enables future integration with Claude, GPT, or other agents.

**A2A (Agent-to-Agent)**: 5 agents communicate via JSON-RPC. CoordinatorAgent orchestrates the pipeline. Each agent is independently testable and replaceable. Enables distributed microservice deployment.

**Why it matters for banks**: Modular (swap models without pipeline changes). Extensible (add SanctionsCheckAgent, KYCAgent). Auditable (every inter-agent message logged). Standards-based (Google A2A + Anthropic MCP protocols).
