"""
Intent Router
Classifies user queries to route to appropriate vector databases.
"""

import google.generativeai as genai
from typing import List, Tuple
import sys
sys.path.insert(0, str(__file__).rsplit('/', 2)[0])

from config.settings import GEMINI_API_KEY, GEMINI_MODEL, INTENT_KEYWORDS
from config.prompts import INTENT_CLASSIFICATION_PROMPT


class IntentRouter:
    """Routes user queries to appropriate knowledge bases."""
    
    # Mapping of intents to collections
    INTENT_TO_COLLECTIONS = {
        "crisis": ["dbt_manual", "nimh_articles"],
        "factual": ["nimh_articles", "cbt_bible"],
        "exercise": ["mind_over_mood", "dbt_manual", "act_simple"],
        "stuck": ["act_simple", "cbt_bible"],
        "cognitive": ["cbt_bible", "mind_over_mood"],
        "general": ["nimh_articles", "cbt_bible", "act_simple"],
    }
    
    def __init__(self, use_llm: bool = False):
        """
        Initialize the router.
        
        Args:
            use_llm: If True, use LLM for classification. If False, use keywords.
        """
        self.use_llm = use_llm
        self.intent_keywords = INTENT_KEYWORDS
        
        if use_llm and GEMINI_API_KEY:
            genai.configure(api_key=GEMINI_API_KEY)
            self.model = genai.GenerativeModel(GEMINI_MODEL)
    
    def classify_keyword(self, message: str) -> str:
        """
        Classify intent using keyword matching.
        
        Args:
            message: User message
            
        Returns:
            Intent category
        """
        message_lower = message.lower()
        
        # Score each intent
        scores = {}
        for intent, keywords in self.intent_keywords.items():
            score = sum(1 for kw in keywords if kw in message_lower)
            scores[intent] = score
        
        # Return highest scoring intent, or 'general' if no matches
        if max(scores.values()) > 0:
            return max(scores, key=scores.get)
        return "general"
    
    def classify_llm(self, message: str) -> str:
        """
        Classify intent using LLM.
        
        Args:
            message: User message
            
        Returns:
            Intent category
        """
        try:
            prompt = INTENT_CLASSIFICATION_PROMPT.format(message=message)
            response = self.model.generate_content(prompt)
            intent = response.text.strip().lower()
            
            # Validate intent
            valid_intents = list(self.INTENT_TO_COLLECTIONS.keys())
            if intent in valid_intents:
                return intent
            return "general"
        except Exception as e:
            print(f"LLM classification failed: {e}")
            return self.classify_keyword(message)
    
    def classify(self, message: str) -> str:
        """
        Classify user message intent.
        
        Args:
            message: User message
            
        Returns:
            Intent category
        """
        if self.use_llm:
            return self.classify_llm(message)
        return self.classify_keyword(message)
    
    def get_collections(self, message: str) -> List[str]:
        """
        Get the collections to query for a given message.
        
        Args:
            message: User message
            
        Returns:
            List of collection names to query
        """
        intent = self.classify(message)
        collections = self.INTENT_TO_COLLECTIONS.get(intent, ["nimh_articles"])
        return collections
    
    def route(self, message: str) -> Tuple[str, List[str]]:
        """
        Route a message and return intent + collections.
        
        Args:
            message: User message
            
        Returns:
            Tuple of (intent, collection_names)
        """
        intent = self.classify(message)
        collections = self.INTENT_TO_COLLECTIONS.get(intent, ["nimh_articles"])
        return intent, collections


# Singleton
_router = None

def get_router(use_llm: bool = False) -> IntentRouter:
    """Get the singleton router instance."""
    global _router
    if _router is None:
        _router = IntentRouter(use_llm=use_llm)
    return _router
