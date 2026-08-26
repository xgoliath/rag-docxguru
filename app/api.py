from fastapi import FastAPI, UploadFile, File
from pathlib import Path
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from .rag import ask_question
from .ingestion import ingest_document
from .retrieval import get_vectorstore
import logging
import os

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)

app = FastAPI(title="DocxGuru API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DOCUMENTS_DIR = Path("documents")
DOCUMENTS_DIR.mkdir(exist_ok=True)


class ChatRequest(BaseModel):
    question: str
    sources: list[str] | None = None


@app.middleware("http")
async def log_requests(request, call_next):
    logger.info("REQUEST START: %s %s", request.method, request.url.path)

    try:
        response = await call_next(request)
        logger.info(
            "REQUEST END: %s %s -> %s",
            request.method,
            request.url.path,
            response.status_code
        )
        return response

    except Exception:
        logger.exception(
            "REQUEST FAILED: %s %s",
            request.method,
            request.url.path
        )
        raise


@app.get("/documents")
def documents():

    logger.info("DOCUMENTS: getting vectorstore")

    vectorstore = get_vectorstore()

    logger.info("DOCUMENTS: vectorstore loaded")

    data = vectorstore.get()

    sources = sorted(set(
        metadata.get("source", "Unknown")
        for metadata in data["metadatas"]
    ))

    logger.info("DOCUMENTS: found %d documents", len(sources))

    return {
        "documents": sources,
        "count": len(sources)
    }


@app.get("/health")
def health():
    logger.info("HEALTH CHECK")
    return {"status": "ok"}


@app.post("/chat")
def chat(request: ChatRequest):

    logger.info("CHAT: question received")

    result = ask_question(
        request.question,
        sources=request.sources
    )

    logger.info("CHAT: answer generated")

    return {
        "answer": result["answer"],
        "sources": result["sources"]
    }


@app.post("/upload")
async def upload(file: UploadFile = File(...)):

    logger.info("UPLOAD: request received")
    logger.info("UPLOAD: filename=%s", file.filename)

    file_path = DOCUMENTS_DIR / file.filename

    logger.info("UPLOAD: reading file")

    contents = await file.read()

    logger.info(
        "UPLOAD: file read successfully, size=%d bytes",
        len(contents)
    )

    with open(file_path, "wb") as f:
        f.write(contents)

    logger.info("UPLOAD: file saved to %s", file_path)

    logger.info("UPLOAD: starting ingestion")

    chunks = ingest_document(str(file_path))

    logger.info(
        "UPLOAD: ingestion completed, chunks=%d",
        chunks
    )

    return {
        "filename": file.filename,
        "chunks": chunks
    }


@app.delete("/documents/{filename}")
def delete_document(filename: str):

    logger.info("DELETE: %s", filename)

    vectorstore = get_vectorstore()

    data = vectorstore.get(
        where={"source": filename}
    )

    ids = data["ids"]

    if ids:
        vectorstore.delete(ids=ids)

    file_path = DOCUMENTS_DIR / filename

    if file_path.exists():
        file_path.unlink()

    return {
        "filename": filename,
        "deleted_chunks": len(ids)
    }
