"""Unit tests for the plain Question/Reply chat log (src/chat_log.py)."""

from src import chat_log
from src.models import Message


def test_format_entry():
    assert chat_log.format_entry(" What is it? ", "ABC\n") == "Question: What is it?\nReply: ABC\n\n"


def test_last_user_text_takes_latest_user_message():
    messages = [
        Message(role="system", content="Be brief."),
        Message(role="user", content="First?"),
        Message(role="assistant", content="One."),
        Message(role="user", content="What is it?"),
    ]
    assert chat_log.last_user_text(messages) == "What is it?"


def test_last_user_text_handles_dicts_and_text_blocks():
    messages = [{"role": "user", "content": [{"type": "text", "text": "Hi"}, {"type": "text", "text": "there"}]}]
    assert chat_log.last_user_text(messages) == "Hi\nthere"
    assert chat_log.last_user_text([]) == ""


def test_log_exchange_appends_pairs(tmp_path):
    path = tmp_path / "sub" / "chat.log"
    messages = [Message(role="user", content="What is it?")]
    chat_log.log_exchange(messages, "ABC", path=str(path))
    chat_log.log_exchange(messages, "ABC", path=str(path))
    assert path.read_text(encoding="utf-8") == (
        "Question: What is it?\nReply: ABC\n\n" "Question: What is it?\nReply: ABC\n\n"
    )


def test_log_exchange_off_without_path(monkeypatch, tmp_path):
    monkeypatch.delenv("CHAT_LOG_FILE", raising=False)
    monkeypatch.chdir(tmp_path)
    chat_log.log_exchange([Message(role="user", content="Q")], "R")
    assert list(tmp_path.iterdir()) == []
