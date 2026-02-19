# Hosting Guide -- AuditWatch SAR Narrative Generator

How to deploy AuditWatch to a server or cloud platform so others can access it remotely.

---

## Option 1: Streamlit Community Cloud (Fastest, Free)

Best for demos and hackathon presentations.

### Steps

1. **Push to GitHub** (public or private repo)

2. **Go to** https://share.streamlit.io

3. **Click "New app"** and fill in:
   - Repository: `your-username/barclays_SAR`
   - Branch: `main`
   - Main file path: `project_files/src/ui/app.py`

4. **Add secrets** in the Streamlit Cloud dashboard:
   - Go to app Settings > Secrets
   - Add:
     ```toml
     JWT_SECRET = "your-secret-key"
     ADMIN_PASSWORD = "AuditWatch2026"
     ```

5. **Click Deploy**

### Limitations

- No Ollama (LLM) on Streamlit Cloud -- the app will use the fallback template narrative.
- Free tier: limited resources, app sleeps after inactivity.
- Good enough for demos.

---

## Option 2: Railway (Recommended for Full Stack)

Supports both the Streamlit app and Ollama.

### Steps

1. **Create account** at https://railway.app

2. **Install Railway CLI:**

   ```bash
   npm install -g @railway/cli
   railway login
   ```

3. **Create a `Procfile`** in `project_files/`:

   ```
   web: streamlit run src/ui/app.py --server.port $PORT --server.address 0.0.0.0
   ```

4. **Create a `runtime.txt`:**

   ```
   python-3.11.7
   ```

5. **Deploy:**

   ```bash
   cd project_files
   railway init
   railway up
   ```

6. **Set environment variables** in Railway dashboard:
   ```
   JWT_SECRET=your-secret-key
   ADMIN_PASSWORD=AuditWatch2026
   OLLAMA_BASE_URL=http://your-ollama-service:11434
   ```

### For Ollama on Railway

- Add a second Railway service using the `ollama/ollama` Docker image.
- Link the two services via Railway's internal networking.
- Set `OLLAMA_BASE_URL` to the internal service URL.

---

## Option 3: Render (Free Tier Available)

### Steps

1. **Create account** at https://render.com

2. **Create a `render.yaml`** in repo root:

   ```yaml
   services:
     - type: web
       name: AuditWatch
       runtime: python
       buildCommand: pip install -r project_files/requirements.txt
       startCommand: cd project_files && streamlit run src/ui/app.py --server.port $PORT --server.address 0.0.0.0
       envVars:
         - key: JWT_SECRET
           sync: false
         - key: ADMIN_PASSWORD
           sync: false
   ```

3. **Connect your GitHub repo** on render.com and deploy.

4. **Add environment variables** in the Render dashboard.

### Limitations

- Free tier spins down after 15 min of inactivity.
- No Ollama support on free tier (use fallback narrative).

---

## Option 4: Docker (Self-Hosted)

For running on your own server or VPS.

### Create `Dockerfile` in `project_files/`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "src/ui/app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

### Build and run:

```bash
cd project_files
docker build -t AuditWatch .
docker run -p 8501:8501 \
  -e JWT_SECRET=your-secret-key \
  -e ADMIN_PASSWORD=AuditWatch2026 \
  AuditWatch
```

### Docker Compose (with Ollama):

Create `docker-compose.yml`:

```yaml
version: "3.8"
services:
  ollama:
    image: ollama/ollama:latest
    ports:
      - "11434:11434"
    volumes:
      - ollama_data:/root/.ollama

  AuditWatch:
    build: ./project_files
    ports:
      - "8501:8501"
    environment:
      - JWT_SECRET=your-secret-key
      - ADMIN_PASSWORD=AuditWatch2026
      - OLLAMA_BASE_URL=http://ollama:11434
    depends_on:
      - ollama

volumes:
  ollama_data:
```

Run: `docker-compose up -d`

Then pull the model: `docker exec -it <ollama-container-id> ollama pull llama3.1:8b`

---

## Option 5: Ngrok (Quick Tunneling for Demo Day)

Expose your local machine to the internet in seconds.

### Steps

1. **Install ngrok:** https://ngrok.com/download

2. **Start the app locally:**

   ```bash
   cd project_files
   streamlit run src/ui/app.py
   ```

3. **In another terminal, start ngrok:**

   ```bash
   ngrok http 8501
   ```

4. **Share the ngrok URL** (e.g., `https://abc123.ngrok-free.app`) with judges.

### Pros

- Zero deployment needed.
- Uses your local Ollama (full LLM capability).
- URL works for anyone with internet access.

### Cons

- Requires your laptop to stay running.
- Free ngrok URLs change each session.
- Latency depends on your internet connection.

---

## Which Option Should I Choose?

| Scenario                   | Recommendation                              |
| -------------------------- | ------------------------------------------- |
| Hackathon demo day         | **Ngrok** (fastest, uses local LLM)         |
| Quick share with judges    | **Streamlit Cloud** (no server needed)      |
| Production-like deployment | **Docker** or **Railway**                   |
| Budget: zero               | **Streamlit Cloud** or **Render free tier** |
| Need full LLM capability   | **Docker Compose** or **Ngrok**             |

---

## Environment Variables Reference

| Variable             | Required | Default                                   | Description                |
| -------------------- | -------- | ----------------------------------------- | -------------------------- |
| `JWT_SECRET`         | Yes      | `default-jwt-secret-change-in-production` | Secret key for JWT signing |
| `ADMIN_PASSWORD`     | No       | `AuditWatch2026`                            | Admin account password     |
| `ADMIN_USER`         | No       | `admin`                                   | Admin username             |
| `OLLAMA_BASE_URL`    | No       | `http://localhost:11434`                  | Ollama server URL          |
| `OLLAMA_MODEL`       | No       | `llama3.1:8b`                             | LLM model name             |
| `CHROMA_PERSIST_DIR` | No       | `./chroma_db`                             | ChromaDB storage path      |
| `LOG_LEVEL`          | No       | `INFO`                                    | Logging level              |

---

## Security Notes for Production

1. **Change all default passwords** before deploying publicly.
2. **Set a strong `JWT_SECRET`** (use `python -c "import secrets; print(secrets.token_hex(32))"`).
3. **Enable HTTPS** via your hosting provider or a reverse proxy (nginx/caddy).
4. **Restrict port access** -- only expose port 8501 (or your chosen port).
5. **Review `.env`** -- ensure it is in `.gitignore` and not committed to the repo.
