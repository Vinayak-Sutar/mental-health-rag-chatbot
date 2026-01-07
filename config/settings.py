# Mental Health RAG Chatbot Configuration

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Paths
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
DATASET_DIR = BASE_DIR / "dataset"
VECTOR_DB_DIR = DATA_DIR / "vector_dbs"
NIMH_DIR = BASE_DIR / "nimh_text_data"

# Gemini API
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = "gemini-2.5-flash"
EMBEDDING_MODEL = "models/embedding-001"

# Vector DB Names
VECTOR_DBS = {
    "cbt_bible": VECTOR_DB_DIR / "cbt_bible",
    "mind_over_mood": VECTOR_DB_DIR / "mind_over_mood",
    "dbt_manual": VECTOR_DB_DIR / "dbt_manual",
    "act_simple": VECTOR_DB_DIR / "act_simple",
    "nimh_articles": VECTOR_DB_DIR / "nimh_articles",
    "counseling": VECTOR_DB_DIR / "counseling",
}

# PDF paths
PDF_SOURCES = {
    "cbt_bible": DATASET_DIR / '"Cognitive Behavior Therapy: Basics and Beyond" by Judith S. Beck.pdf',
    "mind_over_mood": DATASET_DIR / "Mind Over Mood PDF.pdf",
    "dbt_manual": DATASET_DIR / "dbt_skills_training_handouts_and_worksheets_-_linehan_marsha_srg_.pdf",
    "act_simple": DATASET_DIR / "ACT_Made_Simple_Dr._Russ_Harris_preface.pdf",
}

# Counseling data
COUNSELING_CSV = DATASET_DIR / "counseling_conersations.csv"

# Chunking strategies per source
CHUNKING_CONFIG = {
    "cbt_bible": {
        "chunk_size": 1500,
        "chunk_overlap": 200,
        "strategy": "recursive",
    },
    "mind_over_mood": {
        "chunk_size": 800,
        "chunk_overlap": 100,
        "strategy": "recursive",
    },
    "dbt_manual": {
        "chunk_size": 500,
        "chunk_overlap": 50,
        "strategy": "recursive",
    },
    "act_simple": {
        "chunk_size": 1000,
        "chunk_overlap": 150,
        "strategy": "recursive",
    },
    "nimh_articles": {
        "chunk_size": 2000,
        "chunk_overlap": 200,
        "strategy": "full_document",  # Keep articles whole when possible
    },
    "counseling": {
        "chunk_size": None,  # Each Q-A pair is one chunk
        "chunk_overlap": 0,
        "strategy": "qa_pairs",
    },
}

# Retrieval settings
RETRIEVAL_CONFIG = {
    "top_k_per_db": 3,
    "similarity_threshold": 0.7,
    "max_context_tokens": 8000,
    "few_shot_examples": 2,
}

# Intent routing keywords
INTENT_KEYWORDS = {
    "crisis": [
        "panic", "can't breathe", "overwhelming", "out of control",
        "emergency", "urgent", "desperate", "falling apart"
    ],
    "factual": [
        "what is", "what are", "symptoms", "causes", "treatment",
        "medication", "define", "explain", "tell me about"
    ],
    "exercise": [
        "worksheet", "exercise", "practice", "activity", "try",
        "technique", "tool", "help me", "how do i"
    ],
    "stuck": [
        "stuck", "can't change", "nothing works", "pointless",
        "values", "meaning", "purpose", "acceptance"
    ],
    "cognitive": [
        "thoughts", "thinking", "beliefs", "automatic", "distortion",
        "negative", "mindset", "perspective"
    ],
}

# Crisis keywords - IMMEDIATE ABORT
CRISIS_ABORT_KEYWORDS = [
    "suicide", "kill myself", "want to die", "end it all",
    "self-harm", "cut myself", "hurt myself", "end my life",
    "don't want to live", "better off dead", "suicidal"
]

# Crisis response (hardcoded, instant)
CRISIS_RESPONSE = """🆘 **I'm concerned about what you're sharing.**

Your safety is the top priority. Please reach out for immediate support:

📞 **Tele-MANAS**: Call **14416** or **1800-891-4416** (Toll-free, 24/7)
📱 **iCall**: **9152987821**
📱 **Vandrevala Foundation**: **1860-2662-345** (24/7)
🌐 **International**: https://findahelpline.com/

You are not alone. These feelings can get better with support.

If you're in immediate danger, please call **112** or go to your nearest emergency room.

💚 *I'm here when you're ready to talk more.*"""

# Disclaimer
DISCLAIMER = """
---
*I am an AI assistant, not a licensed therapist or doctor. This is informational support, not medical advice. In an emergency, call Tele-MANAS at 14416 or 112.*
"""
