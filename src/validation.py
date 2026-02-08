"""
Validation helpers for grounding/policy-reference checking.
"""

from typing import List
import numpy as np
import difflib


def _cosine_sim(a: np.ndarray, b: np.ndarray) -> float:
    """Cosine similarity between two vectors."""
    if a is None or b is None:
        return 0.0
    denom = (np.linalg.norm(a) * np.linalg.norm(b))
    if denom == 0:
        return 0.0
    return float(np.dot(a, b) / denom)


def assess_groundedness(assessment, context_docs: List, model_name: str = "all-MiniLM-L6-v2", threshold: float = 0.75) -> float:
    """Check if policy_references are grounded in context (0.0-1.0)."""
    policy_refs = getattr(assessment, "policy_references", []) or []
    if not policy_refs:
        return 1.0

    if not context_docs:
        return 0.0

    if hasattr(context_docs[0], 'page_content'):
        context_text = " ".join([d.page_content for d in context_docs if d.page_content]).lower()
    else:
        context_text = " ".join([str(d).lower() for d in context_docs])

    if not context_text:
        return 0.0

    # Try semantic matching first
    try:
        from langchain_huggingface import HuggingFaceEmbeddings
        embedder = HuggingFaceEmbeddings(model_name=model_name)
        doc_texts = [getattr(d, "page_content", str(d)) for d in context_docs]
        doc_embs = embedder.embed_documents(doc_texts)

        grounded_count = 0
        for ref in policy_refs:
            try:
                ref_emb = embedder.embed_query(ref)
            except Exception:
                try:
                    ref_emb = embedder.embed_documents([ref])[0]
                except Exception:
                    ref_emb = None

            best_sim = 0.0
            if ref_emb is not None:
                ref_vec = np.array(ref_emb, dtype=float)
                for doc_vec in doc_embs:
                    try:
                        doc_vec_arr = np.array(doc_vec, dtype=float)
                    except Exception:
                        doc_vec_arr = None
                    sim = _cosine_sim(ref_vec, doc_vec_arr)
                    if sim > best_sim:
                        best_sim = sim

            if best_sim >= threshold:
                grounded_count += 1

        return grounded_count / len(policy_refs)

    except Exception:
        # Fallback: fuzzy matching
        grounded_count = 0
        for ref in policy_refs:
            ref_lower = ref.lower().strip()
            
            if ref_lower in context_text:
                grounded_count += 1
                continue
            
            ratio = difflib.SequenceMatcher(None, ref_lower, context_text).ratio()
            sentences = [s.strip() for s in context_text.split('.')]
            max_sent_ratio = max(
                (difflib.SequenceMatcher(None, ref_lower, sent).ratio() for sent in sentences),
                default=0
            )
            
            if max(ratio, max_sent_ratio) >= threshold:
                grounded_count += 1

        return grounded_count / len(policy_refs) if policy_refs else 1.0