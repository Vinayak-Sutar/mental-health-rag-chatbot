"""
Multi-Source Retriever (LangChain version)
"""

import sys
from pathlib import Path
from typing import List, Dict, Any, Optional

sys.path.insert(0, str(Path(__file__).parent.parent))

from config.settings import RETRIEVAL_CONFIG
from src.vector_store import get_vector_store
from src.router import get_router


class MultiRetriever:
    """Retrieves relevant documents from multiple vector databases."""
    
    def __init__(self):
        self.store = get_vector_store()
        self.router = get_router()
        self.config = RETRIEVAL_CONFIG
    
    def retrieve(
        self,
        query: str,
        collections: Optional[List[str]] = None,
        k: int = 3
    ) -> List[Dict[str, Any]]:
        """Retrieve documents from collections."""
        if collections is None:
            _, collections = self.router.route(query)
        
        all_results = []
        for coll in collections:
            try:
                results = self.store.query(coll, query, k=k)
                for r in results:
                    r["source_collection"] = coll
                all_results.extend(results)
            except Exception as e:
                print(f"Warning: Could not query {coll}: {e}")
        
        # Sort by score (lower is better for L2 distance)
        all_results.sort(key=lambda x: x.get("score", 999))
        return all_results
    
    def retrieve_with_examples(self, query: str) -> Dict[str, Any]:
        """Retrieve context and counseling examples."""
        # Get main context
        _, collections = self.router.route(query)
        context = self.retrieve(query, collections, k=self.config["top_k_per_db"])
        
        # Get counseling examples
        examples = []
        try:
            examples = self.store.query("counseling", query, k=self.config["few_shot_examples"])
        except:
            pass
        
        return {"context": context, "examples": examples}
    
    def format_context(self, docs: List[Dict[str, Any]]) -> str:
        """Format documents into context string."""
        parts = []
        for doc in docs[:10]:  # Limit
            source = doc.get("metadata", {}).get("source", doc.get("source_collection", ""))
            title = doc.get("metadata", {}).get("title", "")
            content = doc.get("content", "")[:2000]  # Truncate
            
            header = f"[{source}"
            if title:
                header += f" - {title}"
            header += "]"
            
            parts.append(f"{header}\n{content}")
        
        return "\n\n---\n\n".join(parts)
    
    def format_examples(self, examples: List[Dict[str, Any]]) -> str:
        """Format counseling examples."""
        parts = []
        for i, ex in enumerate(examples, 1):
            content = ex.get("content", "")[:1500]
            parts.append(f"Example {i}:\n{content}")
        return "\n\n".join(parts)


_retriever = None

def get_retriever() -> MultiRetriever:
    global _retriever
    if _retriever is None:
        _retriever = MultiRetriever()
    return _retriever
