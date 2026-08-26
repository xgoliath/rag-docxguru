import streamlit as st
from pathlib import Path
from html import escape

from rag import ask_question
from ingestion import ingest_document


# --------------------------------------------------
# Configuration
# --------------------------------------------------

st.set_page_config(
    page_title="DocxGuru",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

DOCUMENTS_DIR = Path("documents")
DOCUMENTS_DIR.mkdir(exist_ok=True)


# --------------------------------------------------
# CSS
# --------------------------------------------------

st.markdown(
    """
    <style>

    .stApp {
        background-color: #0a0a0a;
    }

    [data-testid="stSidebar"] {
        background-color: #111111;
        border-right: 1px solid #222222;
    }

    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
        color: #a0a0a0;
        font-size: 0.875rem;
    }

    h1, h2, h3 {
        color: #f5f5f5;
        font-weight: 500;
        letter-spacing: -0.02em;
    }

    p {
        color: #d0d0d0;
        line-height: 1.6;
    }

    .stButton > button {
        background-color: #1a1a1a;
        color: #f5f5f5;
        border: 1px solid #2a2a2a;
        border-radius: 6px;
        padding: 0.5rem 1rem;
        font-weight: 400;
        width: 100%;
    }

    .stButton > button:hover {
        background-color: #252525;
        border-color: #3a3a3a;
    }

    .stChatInput {
        background-color: #0a0a0a;
    }

    .stChatInput > div {
        background-color: #1a1a1a;
        border: 1px solid #2a2a2a;
        border-radius: 8px;
    }

    .stChatInput textarea {
        background-color: #1a1a1a;
        color: #f5f5f5;
        border: none;
    }

    .stChatMessage {
        background-color: transparent;
        border: none;
        padding: 1.5rem 0;
    }

    [data-testid="stChatMessageContent"] {
        color: #d0d0d0;
        line-height: 1.7;
    }

    [data-testid="stFileUploader"] {
        background-color: #1a1a1a;
        border: 1px dashed #2a2a2a;
        border-radius: 6px;
        padding: 1rem;
    }

    .doc-item {
        background-color: #1a1a1a;
        border: 1px solid #2a2a2a;
        border-radius: 6px;
        padding: 0.75rem;
        margin-bottom: 0.5rem;
        font-size: 0.875rem;
        color: #d0d0d0;
    }

    .doc-item-status {
        color: #4ade80;
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }

    .source-item {
        display: inline-block;
        background-color: #1a1a1a;
        border: 1px solid #2a2a2a;
        border-radius: 4px;
        padding: 0.25rem 0.625rem;
        margin-right: 0.5rem;
        margin-bottom: 0.5rem;
        font-size: 0.8125rem;
        color: #a0a0a0;
    }

    .sources-container {
        margin-top: 1rem;
        padding-top: 0.75rem;
        border-top: 1px solid #1a1a1a;
    }

    .sources-label {
        font-size: 0.75rem;
        color: #6b7280;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 0.5rem;
    }

    .empty-state {
        text-align: center;
        padding: 8rem 2rem;
        max-width: 500px;
        margin: 0 auto;
    }

    .empty-title {
        font-size: 1.875rem;
        color: #f5f5f5;
        margin-bottom: 1rem;
        font-weight: 400;
    }

    .empty-description {
        color: #6b7280;
        font-size: 0.9375rem;
        line-height: 1.6;
    }

    .sidebar-brand {
        font-size: 1.25rem;
        font-weight: 500;
        color: #f5f5f5;
        margin-bottom: 0.25rem;
    }

    .sidebar-subtitle {
        font-size: 0.8125rem;
        color: #6b7280;
        margin-bottom: 2rem;
    }

    .section-header {
        font-size: 0.75rem;
        color: #6b7280;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 0.75rem;
        margin-top: 1.5rem;
    }

    #MainMenu,
    footer,
    header {
        visibility: visible;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# --------------------------------------------------
# Session state
# --------------------------------------------------

if "messages" not in st.session_state:
    st.session_state.messages = []

if "active_documents" not in st.session_state:
    st.session_state.active_documents = []


# --------------------------------------------------
# Sidebar
# --------------------------------------------------

with st.sidebar:

    st.html(
        """
        <div class="sidebar-brand">DocxGuru</div>
        <div class="sidebar-subtitle">
            Document intelligence
        </div>
        """
    )

    if st.button("New Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    st.html(
        """
        <div class="section-header">
            Documents
        </div>
        """
    )

    uploaded_files = st.file_uploader(
        "Upload PDF",
        type=["pdf"],
        accept_multiple_files=True,
        label_visibility="collapsed"
    )

    if uploaded_files:

        if st.button(
            "Process Documents",
            type="primary",
            use_container_width=True
        ):

            with st.spinner("Processing documents..."):

                processed = 0

                for uploaded_file in uploaded_files:

                    filename = Path(uploaded_file.name).name
                    file_path = DOCUMENTS_DIR / filename

                    with open(file_path, "wb") as f:
                        f.write(uploaded_file.getvalue())

                    chunks = ingest_document(str(file_path))

                    if filename not in st.session_state.active_documents:
                        st.session_state.active_documents.append(filename)

                    processed += chunks

            st.success(
                f"Documents processed — {processed} chunks"
            )

            st.rerun()

    if st.session_state.active_documents:

        st.html(
            """
            <div class="section-header">
                Active Documents
            </div>
            """
        )

        for doc_name in st.session_state.active_documents:

            safe_doc_name = escape(doc_name)

            st.html(
                f"""
                <div class="doc-item">
                    <div>{safe_doc_name}</div>
                    <div class="doc-item-status">Ready</div>
                </div>
                """
            )


# --------------------------------------------------
# Chat history
# --------------------------------------------------

if not st.session_state.messages:

    st.html(
        """
        <div class="empty-state">

            <div class="empty-title">
                DocxGuru
            </div>

            <div class="empty-description">
                Ask questions about your documents.
            </div>

            <div class="empty-description">
                Upload a PDF from the sidebar to get started.
            </div>

        </div>
        """
    )

else:

    for message in st.session_state.messages:

        with st.chat_message(message["role"]):

            st.markdown(message["content"])

            if message.get("sources"):

                sources_html = (
                    '<div class="sources-container">'
                    '<div class="sources-label">Sources</div>'
                )

                for source in message["sources"]:

                    sources_html += (
                        '<span class="source-item">'
                        f'{escape(source)}'
                        '</span>'
                    )

                sources_html += "</div>"

                st.html(sources_html)


# --------------------------------------------------
# Chat
# --------------------------------------------------

prompt = st.chat_input(
    "Ask a question about your documents"
)

if prompt:

    if not st.session_state.active_documents:

        st.error(
            "Please upload and process a document first."
        )

    else:

        st.session_state.messages.append({
            "role": "user",
            "content": prompt
        })

        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):

            with st.spinner("Thinking..."):

                try:

                    result = ask_question(
                        prompt,
                        sources=st.session_state.active_documents
                    )

                    answer = result["answer"]

                    sources = [
                        f'{item["source"]} — Page {item["page"]}'
                        for item in result["sources"]
                    ]

                    st.markdown(answer)

                    if sources:

                        sources_html = (
                            '<div class="sources-container">'
                            '<div class="sources-label">Sources</div>'
                        )

                        for source in sources:

                            sources_html += (
                                '<span class="source-item">'
                                f'{escape(source)}'
                                '</span>'
                            )

                        sources_html += "</div>"

                        st.html(sources_html)

                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": answer,
                        "sources": sources
                    })

                except Exception as e:

                    st.error(
                        f"Error while processing your question: {e}"
                    )
