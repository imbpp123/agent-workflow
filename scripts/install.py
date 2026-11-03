#!/usr/bin/env python3
"""Link shared skills and merge context hooks. Dry run unless --apply is set."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import shlex
import stat
import sys
import tempfile

ROOT = Path(__file__).resolve().parent.parent
MARKER = "Agent Workflow: load shared skills"


def hook_config(path, repo):
    config = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
    if not isinstance(config, dict):
        raise ValueError("hooks config must be an object")
    hooks = config.setdefault("hooks", {})
    if not isinstance(hooks, dict):
        raise ValueError("hooks must be an object")
    script = repo / "scripts/context_hook.py"
    # Codex command hooks use a shell. Quote both paths, including spaces.
    command = shlex.join([sys.executable, str(script)])
    handler = {"type": "command", "command": command, "timeout": 10,
               "statusMessage": MARKER, "additionalContextLimit": 0}
    for event in ("SessionStart", "UserPromptSubmit"):
        groups = hooks.setdefault(event, [])
        if not isinstance(groups, list):
            raise ValueError("hook event must contain a list")
        owned = []
        for group in groups:
            if not isinstance(group, dict) or not isinstance(group.get("hooks"), list):
                raise ValueError("hook group must contain a hooks list")
            for existing in group["hooks"]:
                if not isinstance(existing, dict):
                    raise ValueError("hook handler must be an object")
                if existing.get("statusMessage") == MARKER:
                    owned.append((group, existing))
        if len(owned) > 1:
            raise ValueError("duplicate Agent Workflow handlers; resolve them before installing")
        if owned:
            group, existing = owned[0]
            if group.get("matcher") not in (None, "", "*") or existing != handler:
                raise ValueError("existing Agent Workflow hook differs; review it before replacing")
        else:
            groups.append({"hooks": [handler.copy()]})
    return config


def plan(target, repo=ROOT):
    target, repo = Path(target).expanduser().resolve(), Path(repo).resolve()
    sources = sorted(p for p in (repo / "skills").iterdir() if p.is_dir() and (p / "SKILL.md").is_file())
    if not sources:
        raise ValueError("no skills found")
    links = []
    for source in sources:
        dest = target / ".agents/skills" / source.name
        if dest.is_symlink() and dest.resolve() == source.resolve():
            continue
        if dest.exists() or dest.is_symlink():
            raise ValueError("skill already exists; no files replaced: " + str(dest))
        links.append((source, dest))
    hooks_file = target / ".codex/hooks.json"
    config = hook_config(hooks_file, repo)
    return links, hooks_file, config


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    mode = stat.S_IMODE(path.stat().st_mode) if path.exists() else 0o600
    fd, tmp = tempfile.mkstemp(prefix=path.name + ".", dir=str(path.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            json.dump(value, stream, ensure_ascii=False, indent=2)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.chmod(tmp, mode)
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def install(target, repo=ROOT, apply=False):
    links, path, config = plan(target, repo)
    if apply:
        for source, dest in links:
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.symlink_to(source, target_is_directory=True)
        if not path.exists() or json.loads(path.read_text(encoding="utf-8")) != config:
            write_json(path, config)
    return {"applied": apply, "new_links": [str(dest) for _, dest in links], "hooks": str(path)}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    scope = parser.add_mutually_exclusive_group(required=True)
    scope.add_argument("--project", type=Path)
    scope.add_argument("--global", dest="user", action="store_true")
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args(argv)
    try:
        if os.name == "nt":
            raise ValueError("automatic hook installation currently supports macOS/Linux; use manual setup on Windows")
        target = Path.home() if args.user else args.project
        if not target.is_dir():
            raise ValueError("target directory must exist")
        print(json.dumps(install(target, apply=args.apply), ensure_ascii=False, indent=2))
        return 0
    except (ValueError, OSError) as error:
        print("install: " + str(error), file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
