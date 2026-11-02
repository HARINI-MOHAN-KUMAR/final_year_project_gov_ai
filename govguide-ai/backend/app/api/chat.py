"""Chat API router – RAG-powered GovGuide Bot with multi-language support."""

from datetime import datetime, timezone
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user, get_optional_user
from app.models.user import User
from app.models.chat import ChatSession, ChatMessage
from app.rag.engine import get_rag
from app.services.llm_service import get_llm_provider
from app.schemas.scheme import ChatMessageCreate, ChatMessageRead, ChatSessionRead

router = APIRouter()


@router.post("/message", response_model=ChatMessageRead, status_code=201,
             summary="Send a message to GovGuide Bot")
async def send_message(
    payload: ChatMessageCreate,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user),
):
    """
    Send a message to the RAG-powered GovGuide Bot.
    Works for both logged-in citizens and anonymous guest users.
    """
    user_text = payload.content

    # RAG retrieval
    rag = get_rag()
    context, sources = rag.get_context_string(user_text, k=3)

    # Language instruction
    lang_instructions = {
        "ta": "Please respond in Tamil (தமிழ்). ",
        "hi": "Please respond in Hindi (हिंदी). ",
        "bn": "Please respond in Bengali (বাংলা). ",
        "en": "",
    }
    lang_note = lang_instructions.get(payload.language, "")

    history_messages = []
    session = None

    # If logged in, manage persistent chat session
    if current_user:
        session_id = payload.session_id
        if session_id:
            result = await db.execute(
                select(ChatSession).where(
                    ChatSession.id == session_id,
                    ChatSession.user_id == current_user.id,
                )
            )
            session = result.scalar_one_or_none()
            if session is None:
                raise HTTPException(status_code=404, detail="Chat session not found")
        else:
            session = ChatSession(
                user_id=current_user.id,
                language=payload.language,
                title=user_text[:50] + ("..." if len(user_text) > 50 else ""),
            )
            db.add(session)
            await db.flush()
            await db.refresh(session)

        # Save user message
        user_msg = ChatMessage(
            session_id=session.id,
            role="user",
            content=user_text,
        )
        db.add(user_msg)
        await db.flush()

        # Build conversation history
        hist_result = await db.execute(
            select(ChatMessage)
            .where(ChatMessage.session_id == session.id)
            .order_by(ChatMessage.created_at.desc())
            .limit(10)
        )
        history = list(reversed(hist_result.scalars().all()))
        history_messages = [
            {"role": m.role, "content": m.content}
            for m in history
            if m.id != user_msg.id
        ]

    prompt_content = (lang_note + user_text) if lang_note else user_text
    history_messages.append({"role": "user", "content": prompt_content})

    # LLM call
    llm = get_llm_provider()
    response_text = await llm.chat(history_messages, context)

    # Save to database if user is logged in
    if current_user and session:
        assistant_msg = ChatMessage(
            session_id=session.id,
            role="assistant",
            content=response_text,
            sources=sources,
            scheme_ids=[s["scheme_id"] for s in sources if isinstance(s, dict) and s.get("scheme_id")],
        )
        db.add(assistant_msg)
        await db.flush()
        await db.refresh(assistant_msg)
        return assistant_msg

    # Guest user response
    return ChatMessageRead(
        id=0,
        role="assistant",
        content=response_text,
        response=response_text,
        sources=sources,
        created_at=datetime.now(timezone.utc),
    )


@router.get("/sessions", response_model=List[ChatSessionRead],
            summary="List all chat sessions")
async def list_sessions(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Return all chat sessions for the current user."""
    result = await db.execute(
        select(ChatSession)
        .where(ChatSession.user_id == current_user.id)
        .order_by(ChatSession.updated_at.desc())
    )
    return result.scalars().all()


@router.get("/sessions/{session_id}", response_model=ChatSessionRead,
            summary="Get a chat session with full message history")
async def get_session(
    session_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Return a single chat session with all messages."""
    result = await db.execute(
        select(ChatSession).where(
            ChatSession.id == session_id,
            ChatSession.user_id == current_user.id,
        )
    )
    session = result.scalar_one_or_none()
    if session is None:
        raise HTTPException(status_code=404, detail="Chat session not found")
    return session


@router.delete("/sessions/{session_id}", status_code=204,
               summary="Delete a chat session")
async def delete_session(
    session_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a chat session and all its messages."""
    result = await db.execute(
        select(ChatSession).where(
            ChatSession.id == session_id,
            ChatSession.user_id == current_user.id,
        )
    )
    session = result.scalar_one_or_none()
    if session is None:
        raise HTTPException(status_code=404, detail="Chat session not found")
    await db.delete(session)
