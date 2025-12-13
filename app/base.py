# app/base.py
from __future__ import annotations
import os
from dataclasses import dataclass
from typing import Any, Dict

# Guard autogen import so the app still runs if it's not installed yet
try:
    from autogen import AssistantAgent  # type: ignore
except Exception:
    class AssistantAgent:  # fallback stub
        def __init__(self, *_, **__): pass
        def generate_reply(self, *_, **__): return "Placeholder response."

# ---- Defaults (so learners never touch env wiring) ----
_AZURE_ENDPOINT_DEFAULT = "http://pluralsight.openai.azure.com"
_AZURE_API_VERSION_DEFAULT = "2024-06-01"
_AZURE_DEPLOYMENT_DEFAULT = "gpt-4o-mini"

def _ensure_defaults() -> None:
    os.environ.setdefault("AZURE_OPENAI_ENDPOINT", _AZURE_ENDPOINT_DEFAULT)
    os.environ.setdefault("AZURE_OPENAI_API_VERSION", _AZURE_API_VERSION_DEFAULT)
    os.environ.setdefault("AZURE_DEPLOYMENT", _AZURE_DEPLOYMENT_DEFAULT)

def azure_autogen_config() -> Dict[str, Any]:
    """Shared AutoGen llm_config."""
    _ensure_defaults()
    return {
        "config_list": [{
            "model": os.getenv("AZURE_DEPLOYMENT", _AZURE_DEPLOYMENT_DEFAULT),
            "api_type": "azure",
            "api_key": os.getenv("AZURE_OPENAI_API_KEY", ""),
            "azure_endpoint": os.getenv("AZURE_OPENAI_ENDPOINT", _AZURE_ENDPOINT_DEFAULT),
            "api_version": os.getenv("AZURE_OPENAI_API_VERSION", _AZURE_API_VERSION_DEFAULT),
        }]
    }

# ---- Keep flask_app.py happy (returns an object; we ignore it later) ----
def build_llm_from_env():
    """Kept for compatibility with flask_app.py; AutoGen uses env directly."""
    _ensure_defaults()
    return {"ok": True}

# ---- QA chain adapter that matches .invoke({'question': ...}).content ----
@dataclass
class _AIMessage:
    content: str

class _AutoGenQAChain:
    def __init__(self):
        self._agent = AssistantAgent(
            name="QAAgent",
            system_message="You answer questions clearly and concisely.",
            llm_config=azure_autogen_config(),
        )

    def invoke(self, payload: Dict[str, Any]) -> _AIMessage:
        q = ((payload or {}).get("question") or "").strip()
        if not q:
            return _AIMessage("Please enter a question.")
        try:
            reply = self._agent.generate_reply(messages=[{"role": "user", "content": q}]) or ""
            text = (reply or "").strip() or "No answer generated."
        except Exception:
            text = "QA (placeholder): This is a demo answer while your setup finishes."
        return _AIMessage(text)

def build_simple_qa_chain(_llm_unused) -> _AutoGenQAChain:
    """Return an AutoGen-backed QA adapter."""
    return _AutoGenQAChain()

# ---- Agent adapter (lazy import of router to avoid circulars) ----
def build_agent(_unused_llm, _tools):
    class _SupportAgentAdapter:
        def invoke(self, payload):
            user_text = ((payload or {}).get("input") or "").strip()
            if not user_text:
                return {"output": "Agent (placeholder): Please enter a message."}
            try:
                from app.router import run_support_flow  # lazy import
                out = run_support_flow(user_text)
                out = (out or "").strip()
                if not out:
                    out = "Agent (placeholder): No output yet."
            except Exception:
                out = "Agent (placeholder): Your agent will respond once the lab steps are complete."
            return {"output": out}
    return _SupportAgentAdapter()
