from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any, Dict

@dataclass
class SimpleSession:
    session_id: str
    state: Dict[str, Any] = field(default_factory=dict)
    touched_at: float = field(default_factory=lambda: time.time())

    def touch(self) -> None:
        self.touched_at = time.time()

_SESSION_STORE: Dict[str, SimpleSession] = {}

def get_session(session_id: str = "default") -> SimpleSession:
    sid = (session_id or "default").strip() or "default"
    sess = _SESSION_STORE.get(sid)
    if sess is None:
        sess = SimpleSession(session_id=sid)
        _SESSION_STORE[sid] = sess
    sess.touch()
    return sess

def sessionize(session=None, session_id: str = "default") -> SimpleSession:
    # If runtime passes a session-like object with `.state`, use it.
    if session is not None and hasattr(session, "state"):
        return session  # type: ignore
    return get_session(session_id=session_id)
