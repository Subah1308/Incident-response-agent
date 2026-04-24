# 🤖 Autonomous SaaS Incident Response System

A multi-agent AI system that autonomously triages, analyzes, and resolves SaaS support incidents using Claude API, RAG with Supabase pgvector, and a 4-agent pipeline.

## Architecture

```
Ticket Input
     ↓
🔍 Triage Agent       → classifies severity (P1-P4) and category
     ↓
📋 Log Analyst Agent  → identifies error patterns and anomalies
     ↓
🧠 Root Cause Agent   → RAG search over past incidents + root cause reasoning
     ↓
✍️ Resolution Agent   → generates customer response + engineering handoff
     ↓
Supabase (stores everything)
```

## Tech Stack
- **Python 3.9+** — agent orchestration
- **Claude API (claude-sonnet-4)** — LLM backbone
- **Supabase pgvector** — vector store for RAG
- **sentence-transformers** — local embeddings (all-MiniLM-L6-v2)
- **FastAPI** — REST backend
- **React** — frontend dashboard

## Setup

### 1. Clone & create virtual environment
```bash
cd incident-response-agent
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure environment variables
```bash
cp .env.example .env
# Edit .env and add your keys
```

### 3. Set up Supabase schema
- Go to your Supabase project → SQL Editor
- Copy and run the entire contents of `setup_supabase.sql`

### 4. Seed the knowledge base
```bash
python3 seed_knowledge_base.py
```

### 5. Start the backend
```bash
uvicorn main:app --reload --port 8000
```

### 6. Start the frontend
```bash
cd frontend
npm install
npm start
```

Open http://localhost:3000

## Usage
1. Enter a support ticket title and description (or load a sample)
2. Click "Run Agent Pipeline"
3. Watch all 4 agents run in sequence
4. Review the full incident report with RAG-grounded root cause
