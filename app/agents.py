# app/agents.py
from typing import Tuple
from autogen import AssistantAgent
from app.base import azure_autogen_config

# Single source of truth for the trigger token (router imports this)
ESCALATE_TOKEN = "[ESCALATE]"


def create_support_and_escalation_agents() -> Tuple[AssistantAgent, AssistantAgent]:
    """
    Return (support_agent, escalation_agent), both using the same Azure config.

    TODOs:
    - SupportAgent system message:
      • Concise Tier-1 answers.
      • If complex/risky/PII/policy/account access needed → emit ESCALATE_TOKEN + one-sentence reason.
      • Otherwise DO NOT mention or describe the token.
    - EscalationAgent system message:
      • Produce a handoff beginning with 'Escalated to human: <one-sentence summary>'.
      • Ask only for essential details needed by a human.
    """
    cfg = azure_autogen_config()

    # TODO: SupportAgent
    support = AssistantAgent(
        name="SupportAgent",
        system_message=(
            "TODO: Concise Tier-1 answers. If complex/risky/PII/policy/account access is needed, "
            f"emit {ESCALATE_TOKEN} plus a short reason. "
            "If you are not escalating, do not mention the token."
        ),
        llm_config=cfg,
    )

    # TODO: EscalationAgent
    escalation = AssistantAgent(
        name="EscalationAgent",
        system_message=(
            "TODO: Acknowledge escalation and produce a brief handoff starting with "
            "'Escalated to human: <one-sentence summary>'. Ask only for essentials."
        ),
        llm_config=cfg,
    )

    return support, escalation
