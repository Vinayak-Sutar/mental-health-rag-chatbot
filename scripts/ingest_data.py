"""
Data Ingestion Script (LangChain version)
Ingests all data sources into ChromaDB.
"""

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import json
import csv
import fitz  # PyMuPDF

from config.settings import (
    PDF_SOURCES, NIMH_DIR, COUNSELING_CSV, CHUNKING_CONFIG, VECTOR_DB_DIR
)
from src.vector_store import get_vector_store


def extract_pdf_text(pdf_path: Path) -> str:
    """Extract text from a PDF file."""
    text = ""
    try:
        doc = fitz.open(pdf_path)
        for page in doc:
            text += page.get_text()
        doc.close()
    except Exception as e:
        print(f"Error extracting PDF {pdf_path}: {e}")
    return text


def chunk_text(text: str, chunk_size: int, overlap: int) -> list:
    """Split text into overlapping chunks."""
    if not text:
        return []
    
    chunks = []
    start = 0
    
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        
        # Try to break at paragraph or sentence
        if end < len(text):
            para_break = chunk.rfind('\n\n')
            if para_break > chunk_size * 0.5:
                chunk = chunk[:para_break]
                end = start + para_break
            else:
                sent_break = max(chunk.rfind('. '), chunk.rfind('.\n'))
                if sent_break > chunk_size * 0.5:
                    chunk = chunk[:sent_break + 1]
                    end = start + sent_break + 1
        
        if chunk.strip():
            chunks.append(chunk.strip())
        start = end - overlap
    
    return chunks


def ingest_pdf(name: str, pdf_path: Path) -> int:
    """Ingest a PDF into its vector database."""
    print(f"\n📚 Processing: {name}")
    
    if not pdf_path.exists():
        print(f"   ❌ File not found: {pdf_path}")
        return 0
    
    # Extract text
    print("   Extracting text...")
    text = extract_pdf_text(pdf_path)
    print(f"   Extracted {len(text)} characters")
    
    if not text:
        return 0
    
    # Get chunking config
    config = CHUNKING_CONFIG.get(name, {"chunk_size": 1000, "chunk_overlap": 100})
    
    # Chunk text
    print(f"   Chunking...")
    chunks = chunk_text(text, config["chunk_size"], config["chunk_overlap"])
    print(f"   Created {len(chunks)} chunks")
    
    if not chunks:
        return 0
    
    # Prepare data
    texts = chunks
    metadatas = [
        {"source": name, "title": pdf_path.stem, "chunk_idx": i}
        for i in range(len(chunks))
    ]
    ids = [f"{name}_{i}" for i in range(len(chunks))]
    
    # Add to vector store
    print("   Adding to vector database...")
    store = get_vector_store()
    store.add_documents(name, texts, metadatas, ids)
    
    print(f"   ✅ Done: {len(chunks)} chunks")
    return len(chunks)


def ingest_nimh() -> int:
    """Ingest NIMH articles."""
    print("\n📰 Processing NIMH Articles")
    
    if not NIMH_DIR.exists():
        print(f"   ❌ Not found: {NIMH_DIR}")
        return 0
    
    # Load metadata
    metadata_path = project_root / "nimh_metadata.json"
    file_meta = {}
    if metadata_path.exists():
        with open(metadata_path) as f:
            for m in json.load(f):
                file_meta[m["filename"]] = m
    
    texts, metadatas, ids = [], [], []
    
    for txt_file in NIMH_DIR.glob("*.txt"):
        try:
            content = txt_file.read_text(encoding="utf-8")
            meta = file_meta.get(txt_file.name, {})
            
            texts.append(content)
            metadatas.append({
                "source": "nimh",
                "filename": txt_file.name,
                "title": meta.get("title", txt_file.stem),
                "topic": meta.get("topic", ""),
                "disorders": ", ".join(meta.get("tags", {}).get("disorders", [])),
            })
            ids.append(f"nimh_{txt_file.stem}")
        except Exception as e:
            print(f"   Warning: {txt_file.name}: {e}")
    
    if texts:
        print(f"   Found {len(texts)} articles")
        store = get_vector_store()
        store.add_documents("nimh_articles", texts, metadatas, ids)
        print(f"   ✅ Done")
    
    return len(texts)


def ingest_counseling() -> int:
    """Ingest counseling conversations."""
    print("\n💬 Processing Counseling Conversations")
    
    if not COUNSELING_CSV.exists():
        print(f"   ❌ Not found: {COUNSELING_CSV}")
        return 0
    
    texts, metadatas, ids = [], [], []
    
    with open(COUNSELING_CSV, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader):
            ctx = row.get("Context", "").strip()
            resp = row.get("Response", "").strip()
            
            if ctx and resp:
                texts.append(f"User: {ctx}\n\nCounselor: {resp}")
                metadatas.append({"source": "counseling", "idx": i})
                ids.append(f"counseling_{i}")
    
    if texts:
        print(f"   Found {len(texts)} conversations")
        store = get_vector_store()
        store.add_documents("counseling", texts, metadatas, ids)
        print(f"   ✅ Done")
    
    return len(texts)


def main():
    print("=" * 60)
    print("🚀 Mental Health RAG - Data Ingestion (LangChain)")
    print("=" * 60)
    
    VECTOR_DB_DIR.mkdir(parents=True, exist_ok=True)
    
    stats = {}
    
    # PDFs
    for name, path in PDF_SOURCES.items():
        stats[name] = ingest_pdf(name, path)
    
    # NIMH
    stats["nimh"] = ingest_nimh()
    
    # Counseling
    stats["counseling"] = ingest_counseling()
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 SUMMARY")
    print("=" * 60)
    for name, count in stats.items():
        icon = "✅" if count > 0 else "❌"
        print(f"   {icon} {name}: {count}")
    print(f"\n   Total: {sum(stats.values())}")


if __name__ == "__main__":
    main()
