from .retrieval import search_documents
from .generation import generate_answer


def ask_question(question: str, sources=None):

    results = search_documents(
        question,
        sources=sources
    )

    documents = [
        document
        for document, score in results
    ]

    context = "\n\n".join(
        document.page_content
        for document in documents
    )

    answer = generate_answer(
        question,
        context
    )

    sources_found = []

    seen = set()

    for document in documents:

        source = document.metadata.get(
            "source",
            "Unknown"
        )

        page = document.metadata.get("page")

        if page is not None:
            page += 1

        source_info = (source, page)

        if source_info not in seen:

            sources_found.append({
                "source": source,
                "page": page
            })

            seen.add(source_info)

    return {
        "answer": answer,
        "sources": sources_found
    }
