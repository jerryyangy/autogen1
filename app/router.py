# app/router.py
from __future__ import annotations
from typing import Tuple
from app.agents import create_support_and_escalation_agents, ESCALATE_TOKEN


def _support_reply(support, user_input: str) -> str:
    """Single-turn call to SupportAgent."""
    # TODO: Call support.generate_reply(...) with the user_input and return trimmed text.
    # messages format: [{"role": "user", "content": user_input}]
    raise NotImplementedError


def _parse_escalation(text: str) -> Tuple[bool, str]:
    """
    Detect the escalation token and extract a brief reason.
    Returns (should_escalate, reason).
    """
    # TODO:
    # - If ESCALATE_TOKEN not in text: return (False, "")
    # - Else return (True, <text after token>.strip() or "No reason provided.")
    raise NotImplementedError


def _escalate(escalation, user_input: str, reason: str) -> str:
    """Ask EscalationAgent for the human-ready handoff."""
    # TODO: Build a short prompt that includes:
    # - The original user_input
    # - The extracted reason
    # - The instruction that the response must start with:
    #   "Escalated to human: <one-sentence summary>"
    # Then call escalation.generate_reply(...) and return trimmed text.
    raise NotImplementedError


def run_support_flow(user_input: str) -> str:
    """
    Support first; escalate only on the token.
    Returns a single display string for the UI.
    """
    # TODO:
    # - Create agents via create_support_and_escalation_agents()
    # - Get Support reply
    # - Parse for escalation; if escalate, call _escalate and return result
    # - Otherwise return the Support reply
    raise NotImplementedError
