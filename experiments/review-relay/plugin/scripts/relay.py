"""Prototype: carry a review to the correction checker without the drafting agent copying it.

Claude Code runs this on PreToolUse (Agent, SubagentHandback) and PostToolUse (Agent).

- Before the spec reviewer starts, save the document it is about to review: the text as reviewed.
  The request's first line must be "Document: <path>".
- When the reviewer finishes, save its report exactly as it returned it.
- Before the correction checker starts, append the saved report and text to its request.
- When the checker finishes, delete what was saved.

Everything is kept in $CLAUDE_PLUGIN_DATA/reviews/<session_id>.json, outside the project. Each
event is also appended to $CLAUDE_PLUGIN_DATA/logs/<session_id>.jsonl so the experiment can check the copies.
"""

import json
import os
import sys

DATA = os.environ.get("CLAUDE_PLUGIN_DATA") or os.path.join(os.path.expanduser("~"), ".relay-data")
# RELAY_MODE=paste (experiment only): record what passes between agents, but inject nothing.
MODE = os.environ.get("RELAY_MODE", "inject")
SESSION = None


def store_path(session):
    return os.path.join(DATA, "reviews", f"{session}.json")


def load(session):
    try:
        with open(store_path(session), encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return None


def save(session, record):
    os.makedirs(os.path.join(DATA, "reviews"), exist_ok=True)
    with open(store_path(session), "w", encoding="utf-8") as f:
        json.dump(record, f)


def log(entry):
    entry["session"] = SESSION
    entry["mode"] = MODE
    os.makedirs(os.path.join(DATA, "logs"), exist_ok=True)
    with open(os.path.join(DATA, "logs", f"{SESSION}.jsonl"), "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")


def is_agent(name, wanted):
    return bool(name) and name.split(":")[-1] == wanted


def document_path(prompt):
    first = (prompt or "").strip().splitlines()[0] if (prompt or "").strip() else ""
    return first[len("Document:"):].strip() if first.startswith("Document:") else None


def response_text(response):
    if isinstance(response, dict):
        blocks = response.get("content") or []
        return "".join(b.get("text", "") for b in blocks if isinstance(b, dict))
    return response if isinstance(response, str) else ""


def wrap(report, path, text):
    return ("\n\n=== REVIEW REPORT ===\n" + report + "\n=== END REVIEW REPORT ===\n\n"
            f"=== DOCUMENT AS REVIEWED: {path} ===\n" + text + "\n=== END DOCUMENT ===\n")


def main():
    event = json.load(sys.stdin)
    name = event.get("hook_event_name")
    tool = event.get("tool_name")
    global SESSION
    session = event.get("session_id", "unknown")
    SESSION = session
    tool_input = event.get("tool_input") or {}
    project = os.environ.get("CLAUDE_PROJECT_DIR") or event.get("cwd") or os.getcwd()

    if tool == "SubagentHandback" and is_agent(event.get("agent_type"), "spec-reviewer"):
        record = load(session) or {}
        record["report"] = tool_input.get("message", "")
        record["via"] = "handback"
        save(session, record)
        log({"event": "handback", "report": record["report"]})
        return 0

    if tool != "Agent":
        return 0
    agent = tool_input.get("subagent_type", "")

    if name == "PreToolUse" and is_agent(agent, "spec-reviewer"):
        path = document_path(tool_input.get("prompt"))
        if not path:
            return 0
        full = path if os.path.isabs(path) else os.path.join(project, path)
        with open(full, encoding="utf-8") as f:
            text = f.read()
        save(session, {"path": path, "text": text})
        log({"event": "review-start", "path": path, "text": text})
        return 0

    if name == "PostToolUse" and is_agent(agent, "spec-reviewer"):
        record = load(session) or {}
        if record.get("via") != "handback":
            record["report"] = response_text(event.get("tool_response"))
            record["via"] = "result"
        save(session, record)
        log({"event": "review-end", "report": record["report"], "via": record["via"],
             "raw_response": event.get("tool_response")})
        return 0

    if name == "PreToolUse" and is_agent(agent, "correction-checker"):
        record = load(session)
        if MODE == "paste":
            log({"event": "checker-start", "original_prompt": tool_input.get("prompt"),
                 "record": record})
            return 0
        if not record or "report" not in record:
            print(json.dumps({"hookSpecificOutput": {
                "hookEventName": "PreToolUse", "permissionDecision": "deny",
                "permissionDecisionReason": "No review is on record for this session, so there is "
                                            "nothing to check corrections against."}}))
            return 0
        full = record["path"] if os.path.isabs(record["path"]) else os.path.join(project, record["path"])
        try:
            with open(full, encoding="utf-8") as f:
                unchanged = f.read() == record["text"]
        except OSError:
            unchanged = False
        if unchanged:
            print(json.dumps({"hookSpecificOutput": {
                "hookEventName": "PreToolUse", "permissionDecision": "deny",
                "permissionDecisionReason": "The document is unchanged since its review. Make the "
                                            "corrections first, then start the checker."}}))
            log({"event": "checker-refused-unchanged"})
            return 0
        updated = dict(tool_input)
        updated["prompt"] = (tool_input.get("prompt") or "") + wrap(
            record["report"], record["path"], record["text"])
        log({"event": "checker-start", "original_prompt": tool_input.get("prompt"),
             "injected_prompt": updated["prompt"]})
        print(json.dumps({"hookSpecificOutput": {
            "hookEventName": "PreToolUse", "permissionDecision": "allow",
            "updatedInput": updated}}))
        return 0

    if name == "PostToolUse" and is_agent(agent, "correction-checker"):
        log({"event": "checker-end", "report": response_text(event.get("tool_response"))})
        try:
            os.remove(store_path(session))
        except OSError:
            pass
        return 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
