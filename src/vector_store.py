"""
Vector Store Manager (LangChain + Chroma)
Handles ChromaDB operations using LangChain.
"""

import sys
from pathlib import Path
from typing import List, Dict, Any, Optional

sys.path.insert(0, str(Path(__file__).parent.parent))

from langchain_chroma import Chroma
from langchain_core.documents import Document

from config.settings import VECTOR_DB_DIR
from src.embeddings import get_embeddings


class VectorStoreManager:
    """Manages multiple Chroma collections for the RAG pipeline."""
    
    def __init__(self):
        """Initialize the vector store manager."""
        VECTOR_DB_DIR.mkdir(parents=True, exist_ok=True)
        self.embeddings = get_embeddings()
        self._stores: Dict[str, Chroma] = {}
    
    def get_store(self, collection_name: str) -> Chroma:
        """Get or create a Chroma store for a collection."""
        if collection_name not in self._stores:
            persist_dir = str(VECTOR_DB_DIR / collection_name)
            self._stores[collection_name] = Chroma(
                collection_name=collection_name,
                embedding_function=self.embeddings,
                persist_directory=persist_dir,
            )
        return self._stores[collection_name]
    
    def add_documents(
        self,
        collection_name: str,
        texts: List[str],
        metadatas: List[Dict[str, Any]],
        ids: List[str]
    ) -> None:
        """Add documents to a collection."""
        store = self.get_store(collection_name)
        
        # Create Document objects
        documents = [
            Document(page_content=text, metadata=meta)
            for text, meta in zip(texts, metadatas)
        ]
        
        # Add in batches
        batch_size = 100
        for i in range(0, len(documents), batch_size):
            batch = documents[i:i+batch_size]
            batch_ids = ids[i:i+batch_size]
            store.add_documents(batch, ids=batch_ids)
            print(f"  Added batch {i//batch_size + 1}/{(len(documents)-1)//batch_size + 1}")
    
    def query(
        self,
        collection_name: str,
        query: str,
        k: int = 3
    ) -> List[Dict[str, Any]]:
        """Query a collection for similar documents."""
        store = self.get_store(collection_name)
        results = store.similarity_search_with_score(query, k=k)
        
        return [
            {
                "content": doc.page_content,
                "metadata": doc.metadata,
                "score": score,
            }
            for doc, score in results
        ]
    
    def get_count(self, collection_name: str) -> int:
        """Get the number of documents in a collection."""
        try:
            store = self.get_store(collection_name)
            return store._collection.count()
        except:
            return 0


# Singleton
_manager = None

def get_vector_store() -> VectorStoreManager:
    """Get the singleton vector store manager."""
    global _manager
    if _manager is None:
        _manager = VectorStoreManager()
    return _manager
