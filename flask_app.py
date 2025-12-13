# flask_app.py
import os
import warnings
from flask import Flask, render_template, request, jsonify, redirect, url_for
from dotenv import load_dotenv

# Reuse your modular code (updated imports)
from app.base import build_llm_from_env, build_simple_qa_chain, build_agent
from app.tools import build_tools

# Suppress LangChain deprecation chatter
try:
    from langchain_core._api.deprecation import LangChainDeprecationWarning
    warnings.filterwarnings("ignore", category=LangChainDeprecationWarning)
except Exception:
    pass

# Point Flask at app/templates
app = Flask(__name__, template_folder="app/templates")
app.secret_key = os.getenv("FLASK_SECRET", "dev-secret-change-me")

# Singletons
_llm = None
_qa_chain = None
_tools = None
_agent = None

ENV_PATH = ".env"


def _load_env():
    """Load .env into process env if present (non-destructive)."""
    load_dotenv(override=False)


def _write_env(kv: dict):
    """Merge-write keys into .env and update process env."""
    existing = {}
    if os.path.exists(ENV_PATH):
        with open(ENV_PATH, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k, v = line.split("=", 1)
                existing[k] = v
    existing.update({k: v for k, v in kv.items() if v})
    with open(ENV_PATH, "w", encoding="utf-8") as f:
        for k, v in existing.items():
            f.write(f"{k}={v}\n")
    load_dotenv(override=True)  # refresh process env


def _need_api_key() -> bool:
    _load_env()
    return not os.getenv("AZURE_OPENAI_API_KEY")


def _ensure_defaults():
    """
    Ensure non-key settings have sensible defaults if missing.
    The UI only asks for API key; we fill the rest.
    """
    _load_env()
    updates = {}
    if not os.getenv("AZURE_OPENAI_ENDPOINT"):
        updates["AZURE_OPENAI_ENDPOINT"] = "http://pluralsight.openai.azure.com"
    if not os.getenv("AZURE_OPENAI_API_VERSION"):
        updates["AZURE_OPENAI_API_VERSION"] = "2024-06-01"
    if not os.getenv("AZURE_DEPLOYMENT"):
        updates["AZURE_DEPLOYMENT"] = "gpt-4o-mini"
    if updates:
        _write_env(updates)


def _reset_singletons():
    global _llm, _qa_chain, _tools, _agent
    _llm = _qa_chain = _tools = _agent = None


def _ensure_initialized():
    """Initialize the LLM, chain, tools, and agent once the key exists."""
    global _llm, _qa_chain, _tools, _agent
    if _need_api_key():
        return  # wait until user provides a key
    if _llm is None:
        _ensure_defaults()
        _llm = build_llm_from_env()
        _qa_chain = build_simple_qa_chain(_llm)
        _tools = build_tools(_llm)      # only smart_summarizer
        _agent = build_agent(_llm, _tools)


def _find_tool(name):
    if not _tools:
        return None
    for t in _tools:
        if t.name == name:
            return t
    return None


def _dispatch(mode, text):
    """
    Return a string result for the selected mode.
    Modes: qa, sum, agent (search removed).
    """
    if mode == "agent":
        return _agent.invoke({"input": text})["output"]
    if mode == "sum":
        tool = _find_tool("smart_summarizer")
        return tool.run(text) if tool else "[Error] smart_summarizer tool not found."
    # default QA
    return _qa_chain.invoke({"question": text}).content


@app.route("/", methods=["GET"])
def index():
    need_key = _need_api_key()
    _ensure_initialized()
    return render_template(
        "index.html",
        mode="qa",
        text="",
        result="" if not need_key else "Enter your Azure API key to begin.",
        need_key=need_key,
    )


@app.route("/save_key", methods=["POST"])
def save_key():
    key = (request.form.get("AZURE_OPENAI_API_KEY") or "").strip()
    if not key:
        return render_template(
            "index.html",
            mode="qa",
            text="",
            result="Please provide a key.",
            need_key=True,
        )
    _write_env({"AZURE_OPENAI_API_KEY": key})
    _reset_singletons()
    return redirect(url_for("index"))


@app.route("/ask", methods=["POST"])
def ask_form():
    need_key = _need_api_key()
    if need_key:
        return render_template(
            "index.html",
            mode="qa",
            text=request.form.get("text") or "",
            result="Enter your API key first.",
            need_key=True,
        )

    _ensure_initialized()

    mode = (request.form.get("mode") or "qa").strip().lower()
    text = (request.form.get("text") or "").strip()

    if not text:
        return render_template(
            "index.html",
            mode=mode,
            text="",
            result="Please enter some text.",
            need_key=False,
        )

    try:
        result = _dispatch(mode, text)
    except Exception as e:
        result = f"[Error] {e}"

    return render_template(
        "index.html",
        mode=mode,
        text=text,
        result=result,
        need_key=False,
    )


@app.route("/api/ask", methods=["POST"])
def ask_api():
    if _need_api_key():
        return jsonify({"ok": False, "error": "API key not set"}), 400
    _ensure_initialized()
    payload = request.get_json(silent=True) or {}
    mode = (payload.get("mode") or "qa").strip().lower()
    text = (payload.get("input") or "").strip()
    if not text:
        return jsonify({"ok": False, "error": "Missing 'input'"}), 400
    try:
        out = _dispatch(mode, text)
        return jsonify({"ok": True, "mode": mode, "input": text, "output": out})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500


@app.route("/health", methods=["GET"])
def health():
    try:
        return jsonify({"ok": True, "need_key": _need_api_key()})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500


if __name__ == "__main__":
    # pip install Flask python-dotenv  (plus your lab deps)
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5000")), debug=True)
