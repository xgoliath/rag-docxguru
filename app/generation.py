import os

from dotenv import load_dotenv
from langchain_groq import ChatGroq


load_dotenv()


def get_llm():
    return ChatGroq(
        model="openai/gpt-oss-120b",
        temperature=0
    )


def generate_answer(question, context):
    llm = get_llm()

    prompt = f"""
You are a helpful assistant answering questions about a document.

Your job is to answer the user's question using ONLY the information
provided in the context.

Rules:

1. Do not use outside knowledge.
2. Do not invent facts that are not present in the context.
3. If the question asks you to compare two or more things, look for
   information about EACH thing in the context and compare them.
4. If the document describes both things but does not explicitly say
   that one is better, clearly state that the document does not
   establish which one is better.
5. You may combine and summarize information from multiple parts of
   the context.
6. Only say "I couldn't find the answer in the document" if the
   context contains no useful information for answering the question.

Context:
{context}

Question:
{question}

Answer:
"""

    response = llm.invoke(prompt)

    return response.content