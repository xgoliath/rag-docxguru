from pathlib import Path

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings


DB_PATH = Path("chroma_db")


def get_embeddings():
    return HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )


def get_vectorstore():
    return Chroma(
        persist_directory=str(DB_PATH),
        embedding_function=get_embeddings()
    )


def document_exists(filename: str):
    vectorstore = get_vectorstore()

    results = vectorstore.get(
        where={"source": filename}
    )

    return len(results["ids"]) > 0


def ingest_document(pdf_path: str):

    filename = Path(pdf_path).name

    # Prevent duplicate ingestion
    if document_exists(filename):
        print(f"{filename} already exists. Skipping ingestion.")
        return 0

    print(f"Loading: {pdf_path}")

    # Load PDF
    loader = PyPDFLoader(pdf_path)
    documents = loader.load()

    print(f"Loaded {len(documents)} pages.")

    # Split document
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )

    chunks = text_splitter.split_documents(documents)

    print(f"Created {len(chunks)} chunks.")

    # Add filename metadata
    for chunk in chunks:
        chunk.metadata["source"] = filename

    # Store in ChromaDB
    vectorstore = get_vectorstore()

    vectorstore.add_documents(chunks)

    print(f"Added {len(chunks)} chunks to ChromaDB.")

    return len(chunks)