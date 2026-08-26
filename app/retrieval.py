from pathlib import Path

from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings


DB_PATH = Path("chroma_db")

RETRIEVAL_K = 8
RELEVANCE_THRESHOLD = 1.85


def get_embeddings():
    return HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )


def get_vectorstore():
    return Chroma(
        persist_directory=str(DB_PATH),
        embedding_function=get_embeddings()
    )


def search_documents(question: str, sources=None, k=RETRIEVAL_K):
    """
    Retrieve documents using similarity search and
    remove results below the relevance threshold.
    """

    vectorstore = get_vectorstore()

    filter_condition = None

    if sources:
        filter_condition = {
            "source": {
                "$in": sources
            }
        }

    results = vectorstore.similarity_search_with_score(
        question,
        k=k,
        filter=filter_condition
    )

    filtered_results = [
        (document, score)
        for document, score in results
        if score <= RELEVANCE_THRESHOLD
    ]

    return filtered_results
