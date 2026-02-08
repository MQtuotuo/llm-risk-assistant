"""
Context retrieval module for similarity search.

This module queries the vector store to retrieve relevant policy and case
documents based on transaction query similarity.
"""

from typing import List
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings


def retrieve_context(query: str, k: int = 4) -> List[Document]:
    """
    Retrieve relevant context documents from the vector store.

    Performs a similarity search on the Chroma vector store to find the k
    most relevant documents (policies or historical cases) related to the
    given query.

    Args:
        query (str): The query string to search for context. Typically a JSON
                    serialized transaction that will be matched against policy
                    and case embeddings.
        k (int, optional): Number of top similar documents to retrieve.
                          Defaults to 4.

    Returns:
        List[Document]: List of k most similar documents from the vector store,
                       ranked by relevance. Each document contains the page
                       content and metadata.
    """
    from pathlib import Path

    # Get the project root
    project_root = Path(__file__).parent.parent
    vectorstore_path = str(project_root / "vectorstore")

    # Use Chroma.from_documents or initialize from persisted db
    db = Chroma(
        persist_directory=vectorstore_path,
        embedding_function=HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    )

    results = db.similarity_search(query, k=k)
    return results