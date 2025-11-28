# LLM Analysis Quiz Solver 🤖

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-green.svg)](https://fastapi.tiangolo.com/)

An intelligent, autonomous agent built with **LangGraph** and **LangChain** that solves complex data-related quizzes involving web scraping, data processing, analysis, and visualization tasks. Powered by **Google Gemini 2.0 Flash**.

---

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Project Structure](#project-structure)
- [Quick Start](#quick-start)
- [Deployment](#deployment)
- [API Documentation](#api-documentation)
- [Tools & Capabilities](#tools--capabilities)
- [Testing](#testing)
- [Troubleshooting](#troubleshooting)
- [License](#license)

---

## 🎯 Overview

This project autonomously solves multi-step quiz tasks that require:

- **Data Sourcing**: Web scraping (JavaScript-rendered), API calls, file downloads
- **Data Preparation**: Cleaning PDFs, CSVs, images, audio, video, JSON, Excel
- **Data Analysis**: Filtering, aggregation, statistical/ML models, geo-spatial analysis
- **Data Visualization**: Charts, narratives, presentations

The system receives quiz URLs via REST API, navigates through chained quizzes, and submits answers automatically within 3-minute time limits.

---

## ✨ Features

- ✅ **Autonomous Multi-Step Solving**: Chains through multiple quiz pages
- ✅ **Dynamic JavaScript Rendering**: Playwright handles client-side pages
- ✅ **Code Generation & Execution**: Writes and runs Python for data tasks
- ✅ **Universal File Support**: PDF, CSV, Image, Audio, Video, JSON, Excel, Text
- ✅ **Self-Installing Dependencies**: Adds required packages on-the-fly
- ✅ **Robust Error Handling**: Retries and time management
- ✅ **Production-Ready**: Docker, Railway, HuggingFace Spaces compatible
- ✅ **Rate Limiting**: Respects Gemini API quotas (9 req/min)

---

## 🏗️ Architecture

```
┌─────────────┐
│   FastAPI   │  ← POST /solve receives quiz URL
│   Server    │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  LangGraph  │  ← State machine orchestrator
│   Agent     │     (Gemini 2.0 Flash)
└──────┬──────┘
       │
       ├────────────┬────────────┬─────────────┬──────────────┐
       ▼            ▼            ▼             ▼              ▼
   [Scraper]   [Downloader]  [Code Exec]  [POST Req]  [Pkg Install]
```

### Key Components

1. **FastAPI Server** (`main.py`): Handles requests, validates secrets
2. **LangGraph Agent** (`agent.py`): Orchestrates tool usage and decision-making
3. **Tools Package** (`tools/`): Modular capabilities (scraping, downloading, etc.)
4. **LLM**: Google Gemini 2.0 Flash with automatic rate limiting

---

## 📁 Project Structure

```
llm-analysis-quiz-solver/
├── main.py                    # FastAPI server
├── agent.py                   # LangGraph state machine
├── requirements.txt           # Python dependencies
├── Dockerfile                 # Container configuration
├── .env.example               # Environment template
├── .gitignore                 # Git ignore rules
├── test_endpoint.py           # Testing script
├── DEPLOYMENT.md              # Deployment guide
├── tools/
│   ├── __init__.py
│   ├── web_scraper.py         # Playwright scraper
│   ├── download_file.py       # File downloader
│   ├── code_generate_and_run.py  # Python executor
│   ├── send_request.py        # HTTP POST tool
│   └── add_dependencies.py    # Package installer
└── README.md                  # This file
```

---

## 🚀 Quick Start

### Prerequisites

- Python 3.12+
- Git
- Railway account (for deployment) OR local environment

### 1. Clone Repository

```bash
git clone https://github.com/yourusername/llm-analysis-quiz-solver.git
cd llm-analysis-quiz-solver
```

### 2. Install Dependencies

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install packages
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium
```

### 3. Configure Environment

Create `.env` file:

```env
EMAIL=your.email@example.com
SECRET=your_secret_from_google_form
GOOGLE_API_KEY=your_gemini_api_key
```

Get Gemini API key: [Google AI Studio](https://aistudio.google.com/app/apikey)

### 4. Run Server

```bash
python main.py
```

Server starts at `http://localhost:7860`

### 5. Test Endpoint

```bash
python test_endpoint.py
```

Or use Thunder Client/curl:

```bash
curl -X POST http://localhost:7860/solve \
  -H "Content-Type: application/json" \
  -d '{
    "email": "your.email@example.com",
    "secret": "your_secret",
    "url": "https://tds-llm-analysis.s-anand.net/demo"
  }'
```

---

## 🌐 Deployment

### Railway (Recommended)

1. **Push to GitHub**

```bash
git add .
git commit -m "Initial commit"
git push origin main
```

2. **Deploy on Railway**
   - Go to [Railway.app](https://railway.app)
   - New Project → Deploy from GitHub repo
   - Select your repository

3. **Configure Environment Variables**
   - Go to **Variables** tab
   - Add: `EMAIL`, `SECRET`, `GOOGLE_API_KEY`, `PORT=7860`

4. **Get Endpoint URL**
   - **Settings** → **Networking** → Generate Domain
   - URL: `https://your-app.up.railway.app/solve`

5. **Submit to Google Form**

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed instructions and other platforms (HuggingFace Spaces, Docker).

---

## 📡 API Documentation

### `POST /solve`

Receives quiz tasks and triggers autonomous agent.

**Request:**

```json
{
  "email": "student@example.com",
  "secret": "secret_string",
  "url": "https://example.com/quiz-123"
}
```

**Responses:**

| Status | Description |
|--------|-------------|
| 200    | Secret verified, agent started |
| 400    | Invalid JSON |
| 403    | Invalid secret |

**Example:**

```bash
curl -X POST https://your-app.up.railway.app/solve \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","secret":"abc123","url":"https://example.com/quiz"}'
```

### `GET /healthz`

Health check endpoint.

**Response:**

```json
{
  "status": "ok",
  "uptime_seconds": 3600
}
```

---

## 🛠️ Tools & Capabilities

### 1. Web Scraper (`get_rendered_html`)

- Renders JavaScript-heavy pages with Playwright
- Waits for network idle
- Returns fully rendered HTML

**Usage:**
```python
html = await get_rendered_html("https://example.com/quiz")
```

### 2. File Downloader (`download_file`)

- Downloads any file type (PDF, CSV, Image, Audio, Video)
- Saves to `LLMFiles/` directory
- Returns filepath

**Usage:**
```python
path = await download_file("https://example.com/data.pdf", "data.pdf")
```

### 3. Code Executor (`run_code`)

- Executes Python code in isolated subprocess
- 60-second timeout
- Returns stdout, stderr, exit code

**Usage:**
```python
result = await run_code("""
import pandas as pd
df = pd.read_csv('LLMFiles/data.csv')
print(df['value'].sum())
""")
```

### 4. HTTP POST (`post_request`)

- Sends JSON payloads to submission endpoints
- Automatic error handling
- Parses responses

**Usage:**
```python
response = await post_request(
    "https://example.com/submit",
    {"email": "...", "secret": "...", "answer": 42}
)
```

### 5. Package Installer (`add_dependencies`)

- Dynamically installs Python packages
- Uses pip with 2-minute timeout

**Usage:**
```python
result = await add_dependencies(["tabula-py", "pdfplumber"])
```

---

## 🧪 Testing

### Automated Tests

```bash
python test_endpoint.py
```

Tests:
1. ✅ Health check
2. ✅ Invalid JSON rejection (400)
3. ✅ Invalid secret rejection (403)
4. ✅ Valid demo quiz submission (200)

### Manual Testing

#### Thunder Client / Postman

1. **Health Check**
   - GET `http://localhost:7860/healthz`
   - Expected: `{"status":"ok",...}`

2. **Invalid Secret**
   - POST `http://localhost:7860/solve`
   - Body: `{"email":"test","secret":"wrong","url":"..."}`
   - Expected: 403

3. **Valid Request**
   - POST `http://localhost:7860/solve`
   - Body: `{"email":"your.email","secret":"your_secret","url":"demo_url"}`
   - Expected: 200, check logs

---

## 🐛 Troubleshooting

### Issue: "Invalid secret" (403)

**Solution:**
- Verify `SECRET` in `.env` matches Google Form submission
- Check for extra spaces/quotes

### Issue: "Module not found"

**Solution:**
```bash
pip install -r requirements.txt
playwright install chromium
```

### Issue: Rate limit errors

**Solution:**
- Gemini Flash: 9 requests/minute
- Agent has automatic rate limiting
- Check API key quota at [Google AI Studio](https://aistudio.google.com/app/apikey)

### Issue: Timeout on quiz

**Solution:**
- Default: 3 minutes per quiz chain
- Check agent logs for stuck points
- Verify network connectivity

### Issue: Playwright browser not found

**Solution:**
```bash
playwright install chromium
playwright install-deps  # Linux only
```

---

## 📊 Supported Data Types

| Type | Libraries | Example |
|------|-----------|---------|
| PDF | PyPDF2, pdfplumber, tabula-py | Table extraction |
| CSV | pandas | Data analysis |
| Excel | openpyxl, xlrd | Spreadsheet processing |
| Images | Pillow, opencv-python | Image analysis |
| Audio | SpeechRecognition | Transcription |
| Video | moviepy, opencv-python | Frame extraction |
| JSON | json | Data parsing |
| Text | Built-in | Text processing |
| Network | networkx | Graph analysis |
| Geo | geopandas, folium | Maps |

---

## 🎓 How It Works

### Workflow

1. **Request Reception**
   - FastAPI receives POST with quiz URL
   - Validates secret
   - Returns 200 OK, starts agent in background

2. **Agent Loop**
   ```
   ┌─→ LLM analyzes state
   │   ↓
   │   Tool execution (scrape/download/code/submit)
   │   ↓
   │   Response evaluation
   │   ↓
   └── Decision (continue or end)
   ```

3. **State Management**
   - All messages stored in state
   - Full history for informed decisions
   - Recursion limit: 200 steps

4. **Completion**
   - Agent returns "END" when no new URL
   - Background task completes
   - Logs show success/failure


---

## 🙏 Acknowledgments

- **Course**: Tools in Data Science (TDS), IIT Madras
- **LLM**: Google Gemini 2.0 Flash
- **Framework**: LangChain, LangGraph
- **Deployment**: Railway

---

## 📧 Contact

For questions or issues:
- Open an issue on GitHub
- Check [DEPLOYMENT.md](DEPLOYMENT.md) for detailed guides
- Contact the owner: Devodita Chakravarty

---
