# AuditWatch -- Complete Setup Guide

Step-by-step instructions, system requirements, and verification checks.

---

## System Requirements

| Component | Minimum                            | Recommended              |
| --------- | ---------------------------------- | ------------------------ |
| CPU       | 4 cores                            | 8 cores                  |
| RAM       | 8 GB                               | 16 GB                    |
| Disk      | 10 GB free                         | 20 GB free               |
| OS        | Windows 10/11, macOS 10.15+, Linux | Same                     |
| Python    | 3.10+                              | 3.11 or 3.12             |
| GPU       | Not required                       | Optional (speeds up LLM) |

---

## Step 1: Install Python (5 min)

Download from https://www.python.org/downloads/

**Windows**: Check "Add Python to PATH" during installation.

Verify:

```bash
python --version
# Expected: Python 3.10.x or higher
```

---

## Step 2: Install Ollama (5 min)

Download from https://ollama.ai/download

**Windows**: Run the installer.
**Mac**: `brew install ollama`
**Linux**: `curl -fsSL https://ollama.ai/install.sh | sh`

Verify:

```bash
ollama --version
```

Pull the default model (~4.7 GB download, one-time):

```bash
ollama pull llama3.1:8b
```

**Alternative models** (set via `OLLAMA_MODEL` in `.env`):

- `llama3.1:8b` -- default, good balance of speed and quality
- `llama3.1:70b` -- higher quality, requires 40GB+ RAM
- `mistral:7b` -- fast alternative
- `gemma2:9b` -- Google's model

---

## Step 3: Clone and Setup (10 min)

```bash
# Clone or extract the project
cd barclays_SAR/project_files

# Create virtual environment
python -m venv venv

# Activate it
# Windows Command Prompt:
venv\Scripts\activate
# Windows PowerShell:
venv\Scripts\Activate.ps1
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

**PowerShell execution policy error?** Run this first:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

---

## Step 4: Configure Environment

```bash
cp .env.example .env
```

Edit `.env`:

```env
JWT_SECRET=your-secret-key-here
ADMIN_USER=admin
ADMIN_PASSWORD=auditwatch2026
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.1:8b
```

For a quick demo, the default values work without changes.

---

## Step 5: Run the Application

**Terminal 1** -- Start Ollama:

```bash
ollama serve
```

**Terminal 2** -- Start the app:

```bash
cd project_files
streamlit run src/ui/app.py
```

The app opens at **http://localhost:8501**.

---

## Step 6: Verify Installation

### Login Credentials

| Username    | Password       | Role              |
| ----------- | -------------- | ----------------- |
| admin       | auditwatch2026 | Full access       |
| analyst_01  | analyst123     | Generate + review |
| reviewer_01 | reviewer123    | Review + approve  |

### Demo Flow

1. Login as `admin`
2. Select `case_003_50lakhs` from the dropdown
3. Click "Generate SAR Narrative"
4. Wait 15-60 seconds (first run is slower)
5. Switch to "Review Narrative" -- check the 5-section narrative
6. Try "Export" tab -- download as PDF, JSON, CSV, or TXT
7. Check "Audit Trail" -- view every logged decision

### Run Automated Tests

```bash
python tests/test_comprehensive.py    # 20 core tests
python tests/test_qa_extended.py      # 23 extended tests
```

Expected: 43/43 tests pass.

---

## Database Setup

AuditWatch uses **SQLite** (Python standard library). No external database setup needed.

- Database file: `./data/sar_engine.db` (auto-created on first run)
- ChromaDB (vector DB): `./chroma_db/` (auto-created on first run)
- Both directories are created automatically -- no manual setup required

To reset the database:

```bash
# Delete and it will be recreated on next run
del data\sar_engine.db       # Windows
rm data/sar_engine.db        # Mac/Linux

# Reset ChromaDB (vector store)
rmdir /s chroma_db           # Windows
rm -rf chroma_db             # Mac/Linux
```

---

## LLM Model Configuration

The model is NOT hardcoded. Change it in `.env`:

```bash
OLLAMA_MODEL=mistral:7b        # Faster alternative
OLLAMA_MODEL=llama3.1:70b      # Higher quality (needs 40GB+ RAM)
OLLAMA_MODEL=gemma2:9b         # Google's model
OLLAMA_MODEL=qwen2:7b          # Alibaba's model
```

Then restart the app. If Ollama is unavailable, the app uses a built-in template-based fallback narrative.

---

## Concurrency Limitations

This is an MVP. Current concurrency constraints:

| Component | Limit                               | Reason                 |
| --------- | ----------------------------------- | ---------------------- |
| Streamlit | 1 process, multiple sessions        | Streamlit architecture |
| SQLite    | Concurrent reads, serialized writes | WAL mode               |
| Ollama    | 1 inference at a time per model     | GPU/CPU constraint     |
| ChromaDB  | Thread-safe reads                   | In-process DB          |

**For 1000+ concurrent reports**, production would need:

- FastAPI + Celery for async task queues
- PostgreSQL for concurrent writes
- Multiple Ollama instances behind a load balancer
- Redis for session management

---

## Troubleshooting

| Problem                     | Solution                                                                       |
| --------------------------- | ------------------------------------------------------------------------------ |
| `python: command not found` | Reinstall Python with "Add to PATH" checked                                    |
| `ollama: command not found` | Restart terminal after installing Ollama                                       |
| Ollama connection refused   | Run `ollama serve` in a separate terminal                                      |
| `ModuleNotFoundError`       | Activate venv: `venv\Scripts\activate`, then `pip install -r requirements.txt` |
| Port 8501 in use            | `streamlit run src/ui/app.py --server.port 8502`                               |
| Slow first generation       | Normal -- LLM cold start + ChromaDB indexing. Subsequent runs are faster       |
| Database errors             | Non-fatal. App uses in-memory fallback. Audit trail still works                |
| ChromaDB errors             | Delete `chroma_db/` and restart                                                |

---

## Time Estimates

| Task                        | Duration      |
| --------------------------- | ------------- |
| Install Python              | 5 min         |
| Install Ollama + pull model | 10-15 min     |
| Setup venv + deps           | 5 min         |
| Configure .env              | 2 min         |
| First test run              | 5 min         |
| **Total**                   | **27-32 min** |
