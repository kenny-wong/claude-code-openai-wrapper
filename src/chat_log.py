"""Plain conversation log (local addition).

When CHAT_LOG_FILE is set, each answered request appends:

    Question: <the request's last user message>
    Reply: <the reply text sent back>

followed by a blank line. The detailed server log is unchanged.
"""

import logging
import os
import threading
from typing import Any, Iterable, Optional

logger = logging.getLogger(__name__)
_lock = threading.Lock()


def _text(content: Any) -> str:
    if content is None:
        return ""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for part in content:
            text = part.get("text") if isinstance(part, dict) else getattr(part, "text", None)
            if text:
                parts.append(text)
        return "\n".join(parts)
    return str(content)


def last_user_text(messages: Optional[Iterable[Any]]) -> str:
    """Text of the last user message (clients resend the whole history each time)."""
    for message in reversed(list(messages or [])):
        role = message.get("role") if isinstance(message, dict) else getattr(message, "role", None)
        if role == "user":
            content = (
                message.get("content") if isinstance(message, dict) else getattr(message, "content", "")
            )
            return _text(content)
    return ""


def format_entry(question: str, reply: str) -> str:
    return f"Question: {(question or '').strip()}\nReply: {(reply or '').strip()}\n\n"


def log_exchange(messages: Optional[Iterable[Any]], reply: Optional[str], path: Optional[str] = None) -> None:
    """Append one Question/Reply pair. Never raises: logging must not break a request."""
    path = path or os.getenv("CHAT_LOG_FILE", "").strip()
    if not path:
        return
    try:
        folder = os.path.dirname(os.path.abspath(path))
        os.makedirs(folder, exist_ok=True)
        entry = format_entry(last_user_text(messages), reply or "")
        with _lock, open(path, "a", encoding="utf-8") as f:
            f.write(entry)
    except Exception as e:  # pragma: no cover - disk problems only
        logger.warning(f"Could not write chat log {path}: {e}")
