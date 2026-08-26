import streamlit as st
from pathlib import Path
from html import escape

from client import (
    ask_question,
    upload_document,
    get_documents,
    delete_document
)


# --------------------------------------------------
# Page configuration
# --------------------------------------------------

st.set_page_config(
    page_title="DocxGuru",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)


# --------------------------------------------------
# Custom CSS
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

    .main {
        background-color: #0a0a0a;
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
        transition: all 0.2s;
        width: 100%;
    }

    .stButton > button:hover {
        background-color: #252525;
        border-color: #3a3a3a;
    }

    .stButton > button:active {
        background-color: #2a2a2a;
    }

    div[data-testid="stVerticalBlock"] > div:has(
        button[kind="primary"]
    ) button,
    .stButton > button[kind="primary"] {
        background-color: #2563eb;
        border-color: #2563eb;
        color: white;
    }

    div[data-testid="stVerticalBlock"] > div:has(
        button[kind="primary"]
    ) button:hover,
    .stButton > button[kind="primary"]:hover {
        background-color: #1d4ed8;
        border-color: #1d4ed8;
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

    .stChatInput textarea:focus {
        border-color: #3a3a3a;
        box-shadow: 0 0 0 1px #3a3a3a;
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

    [data-testid="stChatMessageContent"] p {
        margin-bottom: 0.75rem;
    }

    [data-testid="stFileUploader"] {
        background-color: #1a1a1a;
        border: 1px dashed #2a2a2a;
        border-radius: 6px;
        padding: 1rem;
    }

    [data-testid="stFileUploader"] section {
        border: none;
        padding: 0;
    }

    [data-testid="stFileUploader"] label {
        color: #a0a0a0;
        font-size: 0.875rem;
    }

    hr {
        border-color: #222222;
        margin: 1.5rem 0;
    }

    .doc-item {
        background-color: #1a1a1a;
        border: 1px solid #2a2a2a;
        border-radius: 6px;
        padding: 0.75rem;
        margin-bottom: 0.5rem;
        font-size: 0.875rem;
        color: #d0d0d0;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }

    .doc-item-name {
        flex: 1;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
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
        letter-spacing: -0.02em;
    }

    .empty-description {
        color: #6b7280;
        font-size: 0.9375rem;
        line-height: 1.6;
        margin-bottom: 0.25rem;
    }

    .sidebar-brand {
        font-size: 1.25rem;
        font-weight: 500;
        color: #f5f5f5;
        margin-bottom: 0.25rem;
        letter-spacing: -0.02em;
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

    #MainMenu {
        visibility: hidden;
    }

    footer {
        visibility: hidden;
    }

    header {
        visibility: hidden;
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
# Documents directory
# --------------------------------------------------

DOCUMENTS_DIR = Path("documents")
DOCUMENTS_DIR.mkdir(exist_ok=True)


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

    if st.button(
        "New Chat",
        use_container_width=True
    ):
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

                for uploaded_file in uploaded_files:

                    result = upload_document(
                        uploaded_file
                    )

                    filename = result["filename"]

                    if filename not in st.session_state.active_documents:
                        st.session_state.active_documents.append(
                            filename
                        )

            st.success("Documents processed")
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
                    <div class="doc-item-name">
                        {safe_doc_name}
                    </div>

                    <div class="doc-item-status">
                        Ready
                    </div>
                </div>
                """
            )


# --------------------------------------------------
# Main content
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

            st.markdown(
                message["content"]
            )

            if (
                "sources" in message
                and message["sources"]
            ):

                sources_html = (
                    '<div class="sources-container">'
                    '<div class="sources-label">'
                    'Sources'
                    '</div>'
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
# Chat input
# --------------------------------------------------

prompt = st.chat_input(
    "Ask a question about your documents"
)


if prompt:

    if not st.session_state.active_documents:

        st.error(
            "Please upload and process documents first"
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

                # Ask FastAPI backend
                result = ask_question(
                    prompt,
                    sources=st.session_state.active_documents
                )

                answer = result["answer"]

                # Sources returned by FastAPI
                sources = [
                    f'{item["source"]} — Page {item["page"]}'
                    for item in result["sources"]
                ]

                # Display answer
                st.markdown(answer)

                # --------------------------------------------------
                # Sources
                # --------------------------------------------------

                if sources:

                    sources_html = (
                        '<div class="sources-container">'
                        '<div class="sources-label">'
                        'Sources'
                        '</div>'
                    )

                    for source in sources:

                        sources_html += (
                            '<span class="source-item">'
                            f'{escape(source)}'
                            '</span>'
                        )

                    sources_html += "</div>"

                    st.html(sources_html)

                # Save assistant response
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": answer,
                    "sources": sources
                })
