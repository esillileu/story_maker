import os
import logging
import hashlib
from typing import List, Dict

from pinecone.grpc import PineconeGRPC as pincone
import openai

_pinecone = None
pinecone_index = None


def _init_pinecone():
    global _pinecone, pinecone_index
    if _pinecone is not None:
        return
    api_key = os.getenv("PINECONE_API_KEY")
    environment = os.getenv("PINECONE_ENVIRONMENT")
    _pinecone = pincone(api_key=api_key, environment=environment)
    pinecone_index = _pinecone.Index("test")


embedding_model = "text-embedding-ada-002"


def _hash_embed(text: str, dim: int = 1536) -> List[float]:
    digest = hashlib.sha256(text.encode()).digest()
    values = [b / 255 for b in digest]
    if len(values) >= dim:
        return values[:dim]
    times = dim // len(values) + 1
    values = (values * times)[:dim]
    return values


def _embed(text: str, dim: int = 1536) -> List[float]:
    try:
        api_key = os.getenv("OPENAI_API_KEY")
        client = openai.OpenAI(api_key=api_key)
        response = client.embeddings.create(model=embedding_model, input=text)
        return response.data[0].embedding
    except Exception as e:
        logging.error(f"OpenAI embedding failed: {e}")
        return _hash_embed(text, dim)


def fetch_knowledge(query: str, groups: List[str], top_k: int = 5) -> List[Dict]:
    _init_pinecone()
    vector = _embed(query)
    filter_condition = {"access_group": {"$in": groups}} if groups else None
    try:
        results = pinecone_index.query(vector=vector, top_k=top_k, include_metadata=True, filter=filter_condition)
    except Exception as e:
        logging.error(f"Pinecone query failed: {e}")
        return []
    return [match.metadata for match in getattr(results, "matches", [])]


def update_knowledge(event_summary: str, characters: List[str]) -> List[str]:
    from core.db import get_character

    groups: List[str] = []
    for name in characters:
        char = get_character(name)
        if char:
            groups.extend(char.knowledge_groups)
    groups = list(set(groups))
    knowledges = fetch_knowledge(event_summary, groups)
    return [k.get("description", "") for k in knowledges]


def related_memory(query: str, memories: List[str], top_k: int = 3) -> List[str]:
    """Return memory snippets most relevant to the query."""
    if not memories:
        return []
    q_vec = _embed(query)
    scored = []
    for text in memories:
        m_vec = _embed(text)
        score = sum(a * b for a, b in zip(q_vec, m_vec))
        scored.append((score, text))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [t for _, t in scored[:top_k]]
