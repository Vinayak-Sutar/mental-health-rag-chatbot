"""
Embeddings Module (LangChain)
Uses HuggingFace embeddings via LangChain (FREE, runs locally).
"""

from langchain_huggingface import HuggingFaceEmbeddings

# Default model - fast and good quality
DEFAULT_MODEL = "all-MiniLM-L6-v2"

# Global embeddings instance
_embeddings = None


def get_embeddings(model_name: str = DEFAULT_MODEL) -> HuggingFaceEmbeddings:
    """
    Get or create the embeddings model.
    
    Args:
        model_name: HuggingFace model name
        
    Returns:
        HuggingFaceEmbeddings instance
    """
    global _embeddings
    if _embeddings is None:
        print(f"Loading embedding model: {model_name}...")
        _embeddings = HuggingFaceEmbeddings(
            model_name=model_name,
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )
    return _embeddings
