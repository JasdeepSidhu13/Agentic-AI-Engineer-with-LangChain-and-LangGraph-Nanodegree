import json
import math
import os
import sys

from langchain_core.tools import tool
from langchain_openai import OpenAIEmbeddings
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

_SOLUTION_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if _SOLUTION_ROOT not in sys.path:
    sys.path.insert(0, _SOLUTION_ROOT)

UDAHUB_DB = os.path.join(_SOLUTION_ROOT, "data", "core", "udahub.db")

# In-memory cache for article embeddings (loaded once)
_article_embeddings = None
_embeddings_model = None


def _get_embeddings_model():
    global _embeddings_model
    if _embeddings_model is None:
        _embeddings_model = OpenAIEmbeddings(model="text-embedding-3-small", base_url=os.environ.get("OPENAI_BASE_URL"))
    return _embeddings_model


def _load_articles():
    """Load all knowledge articles from udahub.db and compute embeddings."""
    global _article_embeddings
    if _article_embeddings is not None:
        return _article_embeddings

    from data.models.udahub import Knowledge

    engine = create_engine(f"sqlite:///{UDAHUB_DB}", echo=False)
    Session = sessionmaker(bind=engine)
    session = Session()
    articles = session.query(Knowledge).all()

    model = _get_embeddings_model()
    texts = [f"{a.title}\n{a.content}\nTags: {a.tags}" for a in articles]
    vectors = model.embed_documents(texts)

    _article_embeddings = []
    for article, vector in zip(articles, vectors):
        _article_embeddings.append((
            {
                "article_id": article.article_id,
                "title": article.title,
                "content": article.content,
                "tags": article.tags,
            },
            vector,
        ))
    session.close()
    return _article_embeddings


def _cosine_similarity(a, b):
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(x * x for x in b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


def reset_article_cache():
    """Reset the cached article embeddings. Useful after DB changes."""
    global _article_embeddings
    _article_embeddings = None


@tool
def retrieve_knowledge(query: str) -> str:
    """Search the knowledge base for articles relevant to the query.
    Returns the top 3 most relevant articles with similarity scores.
    Use this to find answers to customer questions about CultPass."""
    articles = _load_articles()
    model = _get_embeddings_model()
    query_vector = model.embed_query(query)

    scored = []
    for article_dict, article_vector in articles:
        score = _cosine_similarity(query_vector, article_vector)
        scored.append((score, article_dict))

    scored.sort(key=lambda x: x[0], reverse=True)
    results = []
    for score, article in scored[:3]:
        results.append({
            "title": article["title"],
            "content": article["content"],
            "tags": article["tags"],
            "relevance_score": round(score, 4),
        })
    return json.dumps(results)
