from fastapi import FastAPI, UploadFile, File
from pathlib import Path
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from .rag import ask_question
from .ingestion import ingest_document
from .retrieval import get_vectorstore


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


@app.get("/documents")
def documents():

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


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/chat")
def chat(request: ChatRequest):

    result = ask_question(
        request.question,
        sources=request.sources
    )

    return {
        "answer": result["answer"],
        "sources": result["sources"]
    }


@app.post("/upload")
async def upload(file: UploadFile = File(...)):

    file_path = DOCUMENTS_DIR / file.filename

    contents = await file.read()

    with open(file_path, "wb") as f:
        f.write(contents)

    chunks = ingest_document(str(file_path))

    return {
        "filename": file.filename,
        "chunks": chunks
    }


@app.delete("/documents/{filename}")
def delete_document(filename: str):

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
