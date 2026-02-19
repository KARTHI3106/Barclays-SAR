# How to Run AuditWatch -- SAR Narrative Generator

Step-by-step instructions to get AuditWatch running on your local machine.

---

## Prerequisites

Before you begin, ensure you have:

| Requirement | Version | Check Command      |
| ----------- | ------- | ------------------ |
| Python      | 3.10+   | `python --version` |
| pip         | Latest  | `pip --version`    |
| Git         | Any     | `git --version`    |
| Ollama      | Latest  | `ollama --version` |

### Install Ollama

Ollama runs the LLM locally (no API keys, no cloud, fully offline).

**Windows:** Download from https://ollama.ai/download and install.
**Mac:** `brew install ollama`
**Linux:** `curl -fsSL https://ollama.ai/install.sh | sh`

---

## Step 1: Clone the Repository

```bash
git clone <your-repo-url>
cd barclays_SAR/project_files
```

---

## Step 2: Create Virtual Environment

**Windows:**

```bash
python -m venv venv
venv\Scripts\activate
```

**Mac/Linux:**

```bash
python3 -m venv venv
source venv/bin/activate
```

Or use the included setup script (Windows):

```bash
SETUP.bat
```

---

## Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

This installs:

- `streamlit` -- web UI framework
- `langchain-ollama` -- LLM integration
- `chromadb` -- vector database for RAG
- `pydantic` -- data validation
- `reportlab` -- PDF generation
- `python-dotenv` -- environment variable loading
- `pyyaml` -- config file parsing

---

## Step 4: Configure Environment

```bash
cp .env.example .env
```

Edit `.env` with your settings:

```
JWT_SECRET=your-secret-key-here
ADMIN_USER=admin
ADMIN_PASSWORD=auditwatch2026
OLLAMA_BASE_URL=http://localhost:11434
```

For a quick demo, the default values work fine.

---

## Step 5: Start Ollama and Pull the Model

Open a **separate** terminal:

```bash
ollama serve
```

Then pull the LLM model:

```bash
ollama pull llama3.1:8b
```

This downloads approximately 4.7 GB. Only needed once.

> **Note:** If Ollama is not running, the app will still work using a built-in fallback template narrative. You do not strictly need Ollama for the demo, but the AI-generated narratives will be much better with it.

---

## Step 6: Run the Application

```bash
cd project_files
streamlit run src/ui/app.py
```

The app opens at **http://localhost:8501**

---

## Step 7: Login

Use one of these demo accounts:

| Username      | Password         | Role                |
| ------------- | ---------------- | ------------------- |
| `admin`       | `auditwatch2026` | Full access         |
| `analyst_01`  | `analyst123`     | Generate and review |
| `reviewer_01` | `reviewer123`    | Review and approve  |

---

## Step 8: Demo Flow

1. **Select a sample case** from the dropdown (e.g., `case_003_50lakhs`)
2. **Click "Generate SAR Narrative"** -- watch the pipeline animation
3. **Switch to "Review Narrative"** -- see the confidence breakdown and compliance checker
4. **Try "Export"** tab -- download as PDF, JSON, CSV, or TXT
5. **Check "Audit Trail"** -- view every decision logged
6. **Visit "Architecture"** -- browse MCP tool servers and A2A agents

---

## Running Tests

```bash
# Core tests (20 checks)
python tests/test_comprehensive.py

# Extended QA tests (23 checks)
python tests/test_qa_extended.py
```

---

## Troubleshooting

### "ModuleNotFoundError" when running

Make sure you are in the `project_files/` directory:

```bash
cd project_files
streamlit run src/ui/app.py
```

### Port 8501 already in use

```bash
streamlit run src/ui/app.py --server.port 8502
```

### Ollama connection refused

1. Check Ollama is running: `ollama serve`
2. Check the URL in `.env`: `OLLAMA_BASE_URL=http://localhost:11434`
3. Test manually: `ollama run llama3.1:8b "hello"`

### ChromaDB errors

Delete the ChromaDB cache and restart:

```bash
# Windows
rmdir /s chroma_db

# Mac/Linux
rm -rf chroma_db
```

### Slow first run

The first run takes longer because ChromaDB needs to index the templates and typology data. Subsequent runs are fast.

---

## Quick One-Liner (after setup)

```bash
cd project_files && streamlit run src/ui/app.py
```
