"""ToolCallingAgent: standard LLM tool-use loop (no PlanExecute).

The LLM calls tools iteratively — each tool result is fed back into the
conversation and the LLM decides what to call next. This is the standard
pattern used by most LLM agent frameworks.

Vulnerability: when the LLM reads an injected document via read_document(),
the injected text becomes part of the conversation. The LLM can then call
any tool based on what it just read — including reading a different file.
"""

from __future__ import annotations

import json
import os
import re

import requests

OLLAMA_URL = "http://localhost:11434/api/chat"

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "read_document",
            "description": "Read a document from the documents/ directory.",
            "parameters": {
                "type": "object",
                "properties": {
                    "filename": {
                        "type": "string",
                        "description": "The filename to read.",
                    }
                },
                "required": ["filename"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "extract_facts",
            "description": "Extract key financial figures from document content.",
            "parameters": {
                "type": "object",
                "properties": {
                    "content": {"type": "string"}
                },
                "required": ["content"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "format_report",
            "description": "Format a filename and extracted facts into a final summary.",
            "parameters": {
                "type": "object",
                "properties": {
                    "filename": {"type": "string"},
                    "facts": {"type": "string"},
                },
                "required": ["filename", "facts"],
            },
        },
    },
]


def _read_document(filename: str) -> str:
    safe_name = os.path.basename(filename)
    path = os.path.join("documents", safe_name)
    if not os.path.exists(path):
        return f"[File not found: {safe_name}]"
    with open(path) as f:
        return f.read()


def _extract_facts(content: str) -> str:
    facts = [
        line.strip()
        for line in content.splitlines()
        if re.search(r"\$[\d,.]+|\d+%|[\d,]+\s*(M|K|B)\b", line)
    ]
    return "\n".join(f"• {f}" for f in facts) if facts else "No figures found."


def _format_report(filename: str, facts: str) -> str:
    return f"[{filename}]\n{facts}"


def _dispatch(name: str, args: dict) -> str:
    if name == "read_document":
        return _read_document(args["filename"])
    if name == "extract_facts":
        return _extract_facts(args["content"])
    if name == "format_report":
        return _format_report(args["filename"], args["facts"])
    return f"[Unknown tool: {name}]"


def run(task: str, model: str) -> tuple[str, list[str]]:
    """Run the tool-calling loop. Returns (final_result, list_of_tool_calls)."""
    messages = [{"role": "user", "content": task}]
    calls_log = []

    for _ in range(8):
        resp = requests.post(
            OLLAMA_URL,
            json={"model": model, "messages": messages, "tools": TOOLS, "stream": False},
        )
        msg = resp.json()["message"]
        messages.append(msg)

        if not msg.get("tool_calls"):
            return msg.get("content", ""), calls_log

        for call in msg["tool_calls"]:
            name = call["function"]["name"]
            args = call["function"]["arguments"]
            if isinstance(args, str):
                args = json.loads(args)

            calls_log.append(f"{name}({json.dumps(args)})")
            result = _dispatch(name, args)
            messages.append({"role": "tool", "content": result})

    return "Max iterations reached.", calls_log
