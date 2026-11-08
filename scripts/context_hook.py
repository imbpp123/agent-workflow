#!/usr/bin/env python3
"""Deliver shared skill text to Codex. No network, state files, or tool approval."""
from __future__ import annotations

import json
from os import PathLike
from pathlib import Path
import re
import sys
from typing import Union

ROOT = Path(__file__).resolve().parent.parent
MAX_CONTEXT_BYTES = 24000
NAME = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*")


def project_paths(cwd: Union[str, PathLike[str]]) -> list[Path]:
    """Return cwd and its parents as paths, stopping at .git or the filesystem root.

    cwd must be an existing directory. The result starts with its resolved path.
    """
    path = Path(cwd).resolve()
    if not path.is_dir():
        raise ValueError("hook cwd must be an existing directory")
    paths = []
    for parent in (path, *path.parents):
        paths.append(parent)
        if (parent / ".git").exists():
            break
    return paths


def settings(paths):
    for path in paths:
        for name in (".agent-workflow.local.json", ".agent-workflow.json"):
            file = path / name
            if file.exists():
                result = json.loads(file.read_text(encoding="utf-8"))
                if not isinstance(result, dict) or set(result) - {"always", "routes"}:
                    raise ValueError("workflow config must contain only always and routes")
                always = result.get("always", [])
                routes = result.get("routes", {})
                if not isinstance(always, list) or not all(isinstance(s, str) for s in always):
                    raise ValueError("always must be a list of skill names")
                if not isinstance(routes, dict):
                    raise ValueError("routes must be an object")
                for name, stems in routes.items():
                    if not isinstance(stems, list) or not stems or not all(
                            isinstance(s, str) and s.strip() for s in stems):
                        raise ValueError("each route needs a nonempty list of words")
                return result
    return {}


def skill_text(repo, name):
    if not isinstance(name, str) or not NAME.fullmatch(name):
        raise ValueError("invalid skill name")
    if name == "go-coding":
        raise ValueError("go-coding was removed; update workflow config to use go-clean-architecture if appropriate and go-code-style")
    if name == "go-architecture":
        raise ValueError("go-architecture was renamed; update workflow config to use go-clean-architecture")
    file = repo / "skills" / name / "SKILL.md"
    text = file.read_text(encoding="utf-8")
    if not text.strip():
        raise ValueError("empty skill: " + name)
    return text


def build_context(event, repo=ROOT):
    if not isinstance(event, dict):
        raise ValueError("hook input must be an object")
    kind = event.get("hook_event_name")
    if kind not in {"SessionStart", "UserPromptSubmit"}:
        raise ValueError("unsupported hook event")
    cwd = event.get("cwd")
    if not isinstance(cwd, str) or not cwd:
        raise ValueError("hook cwd is required")
    paths = project_paths(cwd)
    config = settings(paths)
    names = ["agent-workflow", *config.get("always", [])]

    prompt = event.get("prompt", "")
    if not isinstance(prompt, str):
        raise ValueError("prompt must be a string")
    for name, stems in config.get("routes", {}).items():
        if not NAME.fullmatch(name):
            raise ValueError("invalid route skill name")
        # Validate configured targets even if this prompt does not match.
        skill_text(repo, name)
        if any(re.search(r"(?<!\w)" + re.escape(s.casefold()), prompt.casefold()) for s in stems):
            names.append(name)
    chunks = ["Agent Workflow: skill instructions for this task. Follow project-specific guidance too."]
    for name in dict.fromkeys(names):
        chunks.append("\nSkill: " + name + "\n" + skill_text(repo, name))
    context = "\n".join(chunks)
    if len(context.encode("utf-8")) > MAX_CONTEXT_BYTES:
        raise ValueError("selected skills exceed the hook context limit; shorten skills or routes")
    return {"hookSpecificOutput": {"hookEventName": kind, "additionalContext": context}}


def main():
    try:
        raw = sys.stdin.buffer.read(65537)
        if len(raw) > 65536:
            raise ValueError("hook input exceeds 64 KiB")
        result = build_context(json.loads(raw.decode("utf-8")))
        print(json.dumps(result, ensure_ascii=False))
        return 0
    except (ValueError, OSError) as error:
        print(json.dumps({"systemMessage": "Agent Workflow context was NOT loaded: " + str(error)}))
        return 1


if __name__ == "__main__":
    sys.exit(main())
