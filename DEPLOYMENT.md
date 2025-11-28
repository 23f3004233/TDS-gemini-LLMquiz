# Deployment Guide

## Prerequisites

1. **GitHub Repository**: Create a public repository with MIT License
2. **Google Form**: Fill out the form with your email, secret, and endpoint URL
3. **Gemini API Key**: Get from [Google AI Studio](https://aistudio.google.com/app/apikey)

---

## Option 1: Railway Deployment (Recommended)

### Step 1: Prepare Repository

```bash
git clone <your-repo-url>
cd <your-repo-name>

# Copy all files from this project
# Make sure you have:
# - main.py
# - agent.py
# - tools/ directory with all tool files
# - requirements.txt
# - Dockerfile
# - .gitignore
```

### Step 2: Push to GitHub

```bash
git add .
git commit -m "Initial commit: LLM Analysis Quiz Solver"
git push origin main
```

### Step 3: Deploy on Railway

1. Go to [Railway.app](https://railway.app)
2. Sign in with GitHub
3. Click "New Project" → "Deploy from GitHub repo"
4. Select your repository
5. Railway will auto-detect the Dockerfile

### Step 4: Configure Environment Variables

In Railway dashboard, go to **Variables** tab and add:

```
EMAIL=your.email@example.com
SECRET=your_secret_string
GOOGLE_API_KEY=your_gemini_api_key
PORT=7860
```

### Step 5: Get Your Endpoint URL

1. Go to **Settings** tab
2. Under **Networking**, click "Generate Domain"
3. Your endpoint will be: `https://your-app.up.railway.app/solve`

### Step 6: Submit to Google Form

Use the generated Railway URL in the Google Form.

---

## Option 2: Local Testing

### Step 1: Install Dependencies

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium
```

### Step 2: Configure Environment

Create `.env` file:

```env
EMAIL=your.email@example.com
SECRET=your_secret_string
GOOGLE_API_KEY=your_gemini_api_key
```

### Step 3: Run Server

```bash
python main.py
```

Server starts on `http://localhost:7860`

### Step 4: Test with Demo Quiz

Using Thunder Client or curl:

```bash
curl -X POST http://localhost:7860/solve \
  -H "Content-Type: application/json" \
  -d '{
    "email": "your.email@example.com",
    "secret": "your_secret_string",
    "url": "https://tds-llm-analysis.s-anand.net/demo"
  }'
```

Expected response:
```json
{"status": "ok"}
```

Check terminal logs to see agent solving the quiz.

---

## Option 3: Docker Local Deployment

### Step 1: Build Image

```bash
docker build -t llm-analysis-agent .
```

### Step 2: Run Container

```bash
docker run -p 7860:7860 \
  -e EMAIL="your.email@example.com" \
  -e SECRET="your_secret_string" \
  -e GOOGLE_API_KEY="your_api_key" \
  llm-analysis-agent
```

---

## Option 4: HuggingFace Spaces

### Step 1: Create Space

1. Go to [HuggingFace](https://huggingface.co)
2. Create new Space with Docker SDK
3. Name it (e.g., "llm-analysis-solver")

### Step 2: Configure Space

Add to `README.md` at top:

```yaml
---
title: LLM Analysis Quiz Solver
sdk: docker
app_port: 7860
---
```

### Step 3: Add Secrets

In Space settings, add:
- `EMAIL`
- `SECRET`
- `GOOGLE_API_KEY`

### Step 4: Push Code

```bash
git remote add hf https://huggingface.co/spaces/<username>/<space-name>
git push hf main
```

Your endpoint: `https://<username>-<space-name>.hf.space/solve`

---

## Troubleshooting

### Issue: "Invalid secret" (403)

- Verify `SECRET` in `.env` matches what you submitted in Google Form
- Check for extra spaces or quotes

### Issue: "Module not found"

```bash
pip install -r requirements.txt
```

### Issue: Playwright browser not found

```bash
playwright install chromium
playwright install-deps
```

### Issue: Rate limit errors

- Gemini Flash has 9 requests/minute limit
- Agent automatically handles rate limiting
- If errors persist, check API key quota

### Issue: Timeout on quiz

- Default timeout is 3 minutes per quiz
- Check agent logs for where it's stuck
- Verify network connectivity

---

## Testing Before Evaluation

### Test 1: Health Check

```bash
curl http://localhost:7860/healthz
```

Expected: `{"status":"ok","uptime_seconds":...}`

### Test 2: Invalid Secret

```bash
curl -X POST http://localhost:7860/solve \
  -H "Content-Type: application/json" \
  -d '{"email":"test@test.com","secret":"wrong","url":"https://example.com"}'
```

Expected: HTTP 403

### Test 3: Invalid JSON

```bash
curl -X POST http://localhost:7860/solve \
  -H "Content-Type: application/json" \
  -d 'not json'
```

Expected: HTTP 400

### Test 4: Demo Quiz

```bash
curl -X POST http://localhost:7860/solve \
  -H "Content-Type: application/json" \
  -d '{
    "email": "your.email@example.com",
    "secret": "your_secret",
    "url": "https://tds-llm-analysis.s-anand.net/demo"
  }'
```

Expected: HTTP 200, check logs for quiz solving

---

## Monitoring During Evaluation

### Railway

- Check **Deployments** tab for logs
- Use **Metrics** to monitor CPU/Memory
- Logs show real-time agent activity

### Local

- Terminal shows all logs
- Agent prints:
  - 🌐 URL scraping
  - 📥 File downloads
  - 🐍 Code execution
  - 📮 Answer submission
  - ✅/❌ Results

---

## Important Notes

1. **Evaluation Window**: Sat 29 Nov 2025, 3:00-4:00 PM IST
2. **Time Limit**: 3 minutes per quiz chain
3. **Repository**: Must be public with MIT License
4. **Endpoint**: Must be HTTPS for production (Railway/HF provide this)
5. **Logs**: Keep terminal/Railway logs visible during evaluation

---

## Final Checklist

- [ ] Repository is public on GitHub
- [ ] MIT License file added
- [ ] All code files present (main.py, agent.py, tools/)
- [ ] requirements.txt includes all dependencies
- [ ] Dockerfile configured correctly
- [ ] Environment variables set on deployment platform
- [ ] Endpoint URL submitted in Google Form
- [ ] Tested with demo quiz successfully
- [ ] Verified 403 response for invalid secret
- [ ] Verified 400 response for invalid JSON

---