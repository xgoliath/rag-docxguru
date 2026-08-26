import requests


API_URL = "http://127.0.0.1:2005"


def ask_question(question, sources=None):
    response = requests.post(
        f"{API_URL}/chat",
        json={
            "question": question,
            "sources": sources
        }
    )

    response.raise_for_status()

    return response.json()


def upload_document(file):
    response = requests.post(
        f"{API_URL}/upload",
        files={
            "file": (
                file.name,
                file.getvalue(),
                "application/pdf"
            )
        }
    )

    response.raise_for_status()

    return response.json()


def get_documents():
    response = requests.get(
        f"{API_URL}/documents"
    )

    response.raise_for_status()

    return response.json()


def delete_document(filename):
    response = requests.delete(
        f"{API_URL}/documents/{filename}"
    )

    response.raise_for_status()

    return response.json()
