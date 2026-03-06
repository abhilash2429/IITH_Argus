"""
Chat router — RAG-powered chat over company documents and research.
POST /chat: Ask questions about the credit appraisal.
Uses Qdrant for retrieval and llm_call() for generation.
"""

import uuid
import logging

from fastapi import APIRouter, Body, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database import get_db
from backend.models.db_models import ChatHistory
from backend.agents.llm.llm_client import llm_call
from backend.vector_store.qdrant_client import search_chunks

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/chat")
async def chat_with_cam(
    company_id: str = Body(...),
    message: str = Body(...),
    db: AsyncSession = Depends(get_db),
):
    """
    RAG-powered chat interface over company documents and research.

    Args:
        company_id: UUID of the company.
        message: User's question.
        db: Database session.

    Returns:
        Dict with AI response and source document types.
    """
    # Retrieve relevant chunks from Qdrant
    try:
        relevant_chunks = search_chunks(query=message, company_id=company_id, top_k=5)
        context = "\n\n".join([c["chunk_text"] for c in relevant_chunks])
    except Exception as e:
        logger.warning(f"[Chat] Qdrant search failed: {e}")
        relevant_chunks = []
        context = "No document context available."

    # Build RAG prompt
    prompt = f"""You are a credit analysis assistant for an Indian bank.
Answer questions about this specific company's credit appraisal.
Base your answers ONLY on the provided context (extracted documents and research).
If information is not in the context, say "This information was not found in the available documents."
Be specific — cite which document the information came from.
Use Indian banking terminology (DSCR, MPBF, NPA, DRT, GSTR-3B, CIBIL).

CONTEXT FROM COMPANY DOCUMENTS:
{context}

QUESTION: {message}"""

    # Generate response via LLM
    try:
        response = llm_call(prompt, task="chat_rag", max_tokens=1500)
        response_text = response.text
    except Exception as e:
        logger.error(f"[Chat] LLM call failed: {e}")
        response_text = "I'm sorry, I couldn't process your question. Please try again."

    # Save to chat history
    try:
        sources = list(set(c.get("doc_type", "") for c in relevant_chunks))
        chat_record = ChatHistory(
            id=str(uuid.uuid4()),
            company_id=company_id,
            message=message,
            response=response_text,
            sources=sources,
        )
        db.add(chat_record)
        await db.commit()
    except Exception as e:
        logger.warning(f"[Chat] Failed to save history: {e}")

    return {
        "response": response_text,
        "sources": [c.get("doc_type", "") for c in relevant_chunks],
    }
