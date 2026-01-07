"""
Main RAG Pipeline (with conversation history)
"""

import sys
from pathlib import Path
from typing import Dict, Any, List

sys.path.insert(0, str(Path(__file__).parent.parent))

import google.generativeai as genai

from config.settings import GEMINI_API_KEY, GEMINI_MODEL
from config.prompts import SYSTEM_PROMPT
from src.safety import get_safety_layer
from src.retriever import get_retriever
from src.router import get_router


class RAGPipeline:
    """RAG pipeline with conversation history."""
    
    def __init__(self):
        if not GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY not set in .env")
        
        genai.configure(api_key=GEMINI_API_KEY)
        self.model = genai.GenerativeModel(GEMINI_MODEL)
        
        self.safety = get_safety_layer()
        self.retriever = get_retriever()
        self.router = get_router()
        
        self.history: List[Dict[str, str]] = []
        self.first_message = True
    
    def _format_history(self) -> str:
        """Format conversation history for the prompt."""
        if not self.history:
            return "No previous conversation."
        
        formatted = []
        # Keep last 6 exchanges to avoid token limit
        for msg in self.history[-6:]:
            formatted.append(f"User: {msg['user']}")
            formatted.append(f"You: {msg['assistant']}")
        
        return "\n".join(formatted)
    
    def process(self, message: str) -> Dict[str, Any]:
        """Process user message through RAG pipeline."""
        # Layer 1: Crisis check
        is_crisis, crisis_response = self.safety.check_crisis(message)
        if is_crisis:
            return {
                "response": crisis_response,
                "intent": "crisis",
                "sources": [],
                "is_crisis": True
            }
        
        # Route and retrieve
        intent, _ = self.router.route(message)
        results = self.retriever.retrieve_with_examples(message)
        
        # Format context (limited)
        context = self.retriever.format_context(results["context"][:4])
        examples = self.retriever.format_examples(results["examples"][:2])
        history = self._format_history()
        
        # Build prompt
        prompt = SYSTEM_PROMPT.format(
            context=context or "No specific context needed.",
            few_shot_examples=examples or "",
            history=history,
            user_query=message
        )
        
        # Generate
        try:
            response = self.model.generate_content(prompt)
            text = response.text
        except Exception as e:
            text = f"I'm having a bit of trouble right now. Could you try again? ({str(e)[:50]})"
        
        # Save to history
        self.history.append({"user": message, "assistant": text})
        
        # Sources for metadata
        sources = [
            {
                "source": d.get("source_collection", ""),
                "title": d.get("metadata", {}).get("title", "")
            }
            for d in results["context"][:3]
        ]
        
        self.first_message = False
        
        return {
            "response": text,
            "intent": intent,
            "sources": sources,
            "is_crisis": False
        }
    
    def chat(self, message: str) -> str:
        """Simple chat - returns just response."""
        return self.process(message)["response"]
    
    def reset(self):
        """Reset conversation."""
        self.history = []
        self.first_message = True
    
    def get_history(self) -> List[Dict[str, str]]:
        """Get conversation history."""
        return self.history


_pipeline = None

def get_pipeline() -> RAGPipeline:
    global _pipeline
    if _pipeline is None:
        _pipeline = RAGPipeline()
    return _pipeline
