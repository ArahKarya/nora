"""NORA — query route. Wires to pipeline.orchestrator.answer_query + persists chat."""
from __future__ import annotations
import json

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ..auth.deps import get_current_user
from ..db.database import get_db
from ..db.models import ChatSession, Message, Topic, User

router = APIRouter(prefix="/api", tags=["query"])


class QueryIn(BaseModel):
    topic_id: str
    message: str
    session_id: str | None = None
    top_k: int = 5
    version_filter: str | None = None


@router.post("/query")
def query(
    body: QueryIn,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    topic = db.get(Topic, body.topic_id)
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")

    # resolve / create session (must belong to this user)
    if body.session_id:
        session = db.get(ChatSession, body.session_id)
        if not session or session.user_id != user.id:
            raise HTTPException(status_code=404, detail="Session not found")
    else:
        title = body.message.strip()[:60] or "New chat"
        session = ChatSession(user_id=user.id, topic_id=topic.id, title=title)
        db.add(session)
        db.flush()  # get id

    # call orchestrator (reads ChromaDB via store/config)
    from ..pipeline.orchestrator import answer_query
    from ..pipeline.reason import LLMUnavailable

    try:
        result = answer_query(
            body.message, top_k=body.top_k, version_filter=body.version_filter
        )
    except LLMUnavailable as e:
        raise HTTPException(
            status_code=503,
            detail="Model AI sedang sibuk/overload. Coba lagi sebentar lagi.",
        ) from e
    except Exception as e:  # noqa: BLE001
        raise HTTPException(
            status_code=502,
            detail=f"Gagal memproses pertanyaan: {type(e).__name__}",
        ) from e

    # persist user msg + assistant msg
    user_msg = Message(session_id=session.id, role="user", content=body.message)
    assistant_msg = Message(
        session_id=session.id,
        role="assistant",
        content=result.get("answer", ""),
        sources_json=json.dumps(result.get("sources", []), ensure_ascii=False),
        confidence=result.get("confidence"),
    )
    db.add_all([user_msg, assistant_msg])
    db.commit()

    out = dict(result)
    out["session_id"] = session.id
    return out
