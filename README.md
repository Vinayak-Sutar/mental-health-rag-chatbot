# 🧠 Mental Health Support Chatbot

A RAG-powered mental health support chatbot built with **Gemini API**, **LangChain**, **ChromaDB**, and a **React** frontend.

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![React](https://img.shields.io/badge/React-18-61DAFB)
![License](https://img.shields.io/badge/License-MIT-green)

## Features

- 🤖 **RAG Pipeline** - Retrieves context from 6 specialized databases
- 💬 **Natural Conversations** - Short, empathetic responses like a supportive friend
- 🚨 **Crisis Detection** - Auto-detects crisis keywords and provides 988 hotline
- 📚 **Rich Knowledge Base** - CBT, DBT, ACT therapy books + NIMH articles
- 🎨 **Modern UI** - WhatsApp-inspired React frontend

## Architecture

```
User Query → Crisis Check → Intent Router → Multi-DB Retrieval → Gemini LLM → Response
```

**Data Sources:**
- 4 Therapy Books (CBT, DBT, ACT, Mind Over Mood)
- 173 NIMH Mental Health Articles
- 3,500+ Counseling Conversations (for response style)

## Quick Start

### 1. Clone & Setup

```bash
git clone https://github.com/YOUR_USERNAME/support_chat.git
cd support_chat

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or: venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure API Key

```bash
cp .env.example .env
# Edit .env and add your Gemini API key
```

### 3. Ingest Data

Place your PDF books in `data/books/` and run:

```bash
python scripts/ingest_data.py
```

### 4. Run the App

**Option A: Gradio UI**
```bash
python app.py
# Open http://localhost:7860
```

**Option B: React + FastAPI**
```bash
# Terminal 1: Backend
python api.py

# Terminal 2: Frontend
cd frontend && npm install && npm run dev
# Open http://localhost:5173
```

## Project Structure

```
support_chat/
├── config/
│   ├── settings.py      # Configuration
│   └── prompts.py       # System prompts
├── src/
│   ├── pipeline.py      # Main RAG pipeline
│   ├── retriever.py     # Multi-DB retrieval
│   ├── vector_store.py  # ChromaDB management
│   ├── router.py        # Intent classification
│   └── safety.py        # Crisis detection
├── scripts/
│   └── ingest_data.py   # Data ingestion
├── frontend/            # React UI
├── api.py               # FastAPI backend
├── app.py               # Gradio UI
└── requirements.txt
```

## Tech Stack

- **LLM**: Google Gemini 2.5 Flash
- **Embeddings**: HuggingFace Sentence Transformers (all-MiniLM-L6-v2)
- **Vector DB**: ChromaDB
- **Framework**: LangChain
- **Backend**: FastAPI
- **Frontend**: React + Vite

## Safety Features

- **Crisis Interceptor**: Detects keywords like "suicide", "kill myself" and immediately provides crisis resources
- **988 Lifeline**: US crisis hotline prominently displayed
- **No Diagnosis**: Chatbot never diagnoses or prescribes

## License

MIT License

---

⚠️ **Disclaimer**: This is an AI assistant, not a licensed therapist. For emergencies, call **Tele-MANAS 14416** (India) or **112**.
