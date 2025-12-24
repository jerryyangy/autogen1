#### autogen1
Use Microsoft autogen orchestrator to test &amp; run a Summarizer Tool


### Introduction

Welcome to Multi-Agent Systems with AutoGen.

This is an use case to build a two-agent customer support bot in a Flask app using Microsoft’s AutoGen, backed by Azure OpenAI. It wires up three capabilities: a quick-answer QA path, a summarizer tool (always 3–5 bullets + a TL;DR), and a Support → Escalation flow that routes complex or risky requests to a simulated human tier with a clean handoff.

By the end, the app will:

Answer direct questions via a Simple QA path
Summarize long text into 3–5 bullets with a one-sentence TL;DR
Route support requests through Support → Escalation and produce human-ready handoffs
Outcomes
Content & Learning: Turn long tickets, chats, or transcripts into crisp bullets + TL;DR
Productivity: Auto-triage support requests; generate ready-to-send escalation notes
Compliance & QA: Encode escalation rules (PII, legal, payments, outages) into governed prompts
Pipelines: Reuse the summarizer and escalation logic as building blocks in larger RAG/agent workflows

### Mental Model

Agent: A specialized teammate with a role (system message) and optional tools (e.g., Support vs. Escalation).
Tool: A capability the app can call (e.g., a summarizer that always returns 3–5 bullets + TL;DR).
Router (orchestrator): A traffic controller that sends input to Support first, watches for the [ESCALATE] flag, and—if needed—asks Escalation to draft the human handoff.
Dialogue: A structured conversation between agents that yields one user-facing response (or a handoff).



### Repo Layout (teaching-first split)

```
workspace/
└── app/
    ├── base.py               # provided; env wiring, Azure/AutoGen config, Simple QA adapter, Agent adapter
    ├── agents.py             # Step 1: define Support & Escalation agents + ESCALATE_TOKEN
    ├── router.py             # Step 2: orchestration (Support → optional Escalation, returns final string)
    ├── tools.py              # Step 3: implement "smart_summarizer" (3–5 bullets + TL;DR)
    └── templates/
        └── index.html        # provided UI; no changes needed
flask_app.py                  # provided; handles key, routes, and modes
.env                          # created automatically when you paste your API key in the UI
```
