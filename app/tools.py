# app/tools.py
from __future__ import annotations
from dataclasses import dataclass
from typing import Callable, List
from app.base import azure_autogen_config

# Guarded import so the app still renders in starter mode
try:
    from autogen import AssistantAgent  # type: ignore
except Exception:
    class AssistantAgent:  # fallback stub
        def __init__(self, *_, **__): pass
        def generate_reply(self, *_, **__):
            return "• Placeholder bullet\n• Add more bullets here\n\nTL;DR: Placeholder."

@dataclass
class _SimpleTool:
    name: str
    description: str
    _runner: Callable[[str], str]
    def run(self, text: str) -> str:
        return self._runner(text)

def build_tools(_unused_llm) -> List[_SimpleTool]:
    """
    Starter tool setup for summarization.

    TODOs:
    - Create an AutoGen AssistantAgent with a strong system_message for summarization.
    - Write summarize_text(text: str) -> str that calls agent.generate_reply(...) and returns a string.
    - Wrap summarize_text in a _SimpleTool named 'smart_summarizer' with a clear description.
    - Return a list containing this tool.
    """

    # TODO(1): Build the summarizer agent
    agent = AssistantAgent(
        name="SummarizerAgent",
        system_message=(
            "TODO: Output 3–5 concise, fact-only bullets. "
            "If source names appear, include them. "
            "After the bullets, write one sentence that begins with 'TL;DR:'."
        ),
        llm_config=azure_autogen_config(),
    )

    # TODO(2): Define the runner
    def summarize_text(text: str) -> str:
        text = (text or "").strip()
        if not text:
            return "• Please paste some text to summarize.\n\nTL;DR: No content provided."
        prompt = (
            "Summarize the following content into 3–5 concise bullets, "
            "then add a one-sentence TL;DR line starting with 'TL;DR:'.\n\n"
            f"{text}"
        )
        try:
            reply = agent.generate_reply(messages=[{'role': 'user', 'content': prompt}]) or ""
            out = (reply or "").strip()
            if not out:
                out = "• (no bullets)\n\nTL;DR: Summary unavailable."
        except Exception:
            out = ("• This is a placeholder summary while your setup finishes.\n"
                   "• Replace the TODO system message when ready.\n\nTL;DR: Placeholder output.")
        # Optional guardrail to keep shape predictable
        if "TL;DR:" not in out:
            out += "\n\nTL;DR: Summary unavailable."
        return out

    # TODO(3): Wrap as a tool
    summarizer_tool = _SimpleTool(
        name="smart_summarizer",
        description="Summarize into 3–5 concise bullets and finish with 'TL;DR: ...'.",
        _runner=summarize_text,
    )

    return [summarizer_tool]
