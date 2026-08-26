from ingestion import ingest_document
from rag import ask_question as rag_ask_question
from retrieval import get_vectorstore
from pathlib import Path
import tempfile


def ask_question(question, sources=None):
    return rag_ask_question(
        question,
        sources=sources
    )


def upload_document(file):
    filename = Path(file.name).name

    with tempfile.NamedTemporaryFile(
        delete=False,
        suffix=".pdf"
    ) as temp_file:
        temp_file.write(file.getvalue())
        temp_path = temp_file.name

    try:
        chunks = ingest_document(temp_path)

        return {
            "filename": filename,
            "chunks": chunks
        }

    finally:
        Path(temp_path).unlink(missing_ok=True)


def get_documents():
    vectorstore = get_vectorstore()

    data = vectorstore.get()

    sources = sorted(set(
        metadata.get("source", "Unknown")
        for metadata in data["metadatas"]
    ))

    return {
        "documents": sources,
        "count": len(sources)
    }


def delete_document(filename):
    vectorstore = get_vectorstore()

    data = vectorstore.get(
        where={"source": filename}
    )

    ids = data["ids"]

    if ids:
        vectorstore.delete(ids=ids)

    return {
        "filename": filename,
        "deleted_chunks": len(ids)
    }
