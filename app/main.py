from .retrieval import get_retriever
from .generation import generate_answer


def main():
    retriever = get_retriever()

    question = input("\nAsk a question about the document: ")

    # Retrieve relevant chunks
    documents = retriever.invoke(question)

    # Build context
    context = "\n\n".join(
        document.page_content
        for document in documents
    )

    # Generate answer
    answer = generate_answer(question, context)

    print("\n--- Answer ---\n")
    print(answer)

    # Display unique sources
    print("\n--- Sources ---\n")

    sources = set()

    for document in documents:
        source = document.metadata.get("source", "Unknown")
        page = document.metadata.get("page")

        if page is not None:
            sources.add((source, page + 1))
        else:
            sources.add((source, "Unknown"))

    for source, page in sorted(sources):
        print(f"📄 {source} — Page {page}")


if __name__ == "__main__":
    main()