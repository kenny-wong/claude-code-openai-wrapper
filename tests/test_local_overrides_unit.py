"""Unit tests for the local FORCE_MODEL / DEFAULT_ENABLE_TOOLS overrides in src/models.py."""

from src.models import AnthropicMessagesRequest, ChatCompletionRequest


def _chat(**kwargs):
    return ChatCompletionRequest(messages=[{"role": "user", "content": "Hi"}], **kwargs)


def test_force_model_overrides_client_model(monkeypatch):
    monkeypatch.setenv("FORCE_MODEL", "claude-opus-5-5")
    assert _chat(model="gpt-4o").model == "claude-opus-5-5"
    assert _chat().model == "claude-opus-5-5"
    anthropic = AnthropicMessagesRequest(model="claude-haiku-4-5", messages=[{"role": "user", "content": "Hi"}])
    assert anthropic.model == "claude-opus-5-5"


def test_client_model_kept_without_force(monkeypatch):
    monkeypatch.delenv("FORCE_MODEL", raising=False)
    assert _chat(model="claude-sonnet-5-5").model == "claude-sonnet-5-5"


def test_default_enable_tools(monkeypatch):
    monkeypatch.delenv("DEFAULT_ENABLE_TOOLS", raising=False)
    assert _chat().enable_tools is False
    monkeypatch.setenv("DEFAULT_ENABLE_TOOLS", "true")
    assert _chat().enable_tools is True
    assert _chat(enable_tools=False).enable_tools is False
