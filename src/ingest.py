"""
Vector store ingestion module.

This module handles loading documents (policies and historical cases),
chunking them, embedding them, and storing them in a Chroma vector database
for similarity-based retrieval during risk assessment.
"""

from langchain_community.document_loaders import TextLoader, CSVLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings


def build_vector_store() -> None:
    """
    Build or update the vector store with policy and case data.

    This function:
    1. Loads policy documents (markdown) and historical cases (CSV)
    2. Splits documents into chunks for better retrieval
    3. Generates embeddings for each chunk
    4. Stores vectors in a Chroma database
    5. Persists the database to disk for reuse

    The operation is idempotent - running it multiple times will overwrite
    the existing vector store with fresh embeddings.

    Data sources:
    - data/policies/card_fraud_policy.md: Fraud detection policies
    - data/cases/historical_cases.csv: Historical fraud cases for context

    Returns:
        None
    """
    from pathlib import Path

    # Get the project root (parent of src directory)
    project_root = Path(__file__).parent.parent

    loaders = [
        TextLoader(str(project_root / "data/policies/card_fraud_policy.md")),
        CSVLoader(str(project_root / "data/cases/historical_cases.csv"))
    ]

    docs = []
    for loader in loaders:
        docs.extend(loader.load())

    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = splitter.split_documents(docs)

    vectorstore = Chroma.from_documents(
        chunks,
        #embedding=OpenAIEmbeddings(),
        embedding = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2"),
        persist_directory=str(project_root / "vectorstore")
    )

    vectorstore.persist()

if __name__ == "__main__":
    build_vector_store()
