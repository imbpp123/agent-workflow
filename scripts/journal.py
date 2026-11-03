#!/usr/bin/env python3
"""Local task retros. Python standard library only."""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import datetime as dt
import json
import os
from pathlib import Path
import sqlite3
import sys

KINDS = {"verification", "knowledge", "scope", "intent", "tooling", "collision"}
SCHEMA = """
CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY,
    date TEXT NOT NULL,
    project TEXT NOT NULL,
    area TEXT NOT NULL,
    task_id TEXT NOT NULL,
    task TEXT NOT NULL,
    outcome TEXT NOT NULL CHECK(outcome IN ('accepted', 'abandoned')),
    rounds INTEGER NOT NULL CHECK(rounds >= 0),
    causes TEXT NOT NULL,
    changes TEXT NOT NULL,
    evidence TEXT NOT NULL,
    UNIQUE(project, task_id)
);
"""


def nonempty(value):
    value = value.strip()
    if not value:
        raise ValueError("values must not be blank")
    return value


def cause(value):
    kind, sep, detail = value.partition(":")
    if not sep or kind not in KINDS:
        raise ValueError("cause must be kind:detail; kinds: " + ", ".join(sorted(KINDS)))
    return {"kind": kind, "detail": nonempty(detail)}


def connect(path):
    path = Path(path).expanduser()
    path.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(str(path), timeout=10)
    con.row_factory = sqlite3.Row
    con.executescript(SCHEMA)
    return con


def add(path, *, project, area, task_id, task, rounds, causes=(), changes=(), evidence=(),
        date=None, outcome="accepted"):
    project, area, task_id, task = map(nonempty, (project, area, task_id, task))
    date = date or dt.date.today().isoformat()
    date = dt.date.fromisoformat(date).isoformat()
    if outcome not in {"accepted", "abandoned"}:
        raise ValueError("unknown outcome")
    if rounds < 0 or len(causes) != rounds:
        raise ValueError("rounds must be nonnegative with one cause per round")
    parsed = [cause(item) for item in causes]
    changes = [nonempty(item) for item in changes]
    evidence = [nonempty(item) for item in evidence]
    if rounds and (not changes or not evidence):
        raise ValueError("a retro with returns needs a change and evidence")
    con = connect(path)
    try:
        with con:
            cur = con.execute(
                "INSERT INTO tasks(date,project,area,task_id,task,outcome,rounds,causes,changes,evidence) "
                "VALUES (?,?,?,?,?,?,?,?,?,?)",
                (date, project, area, task_id, task, outcome, rounds,
                 json.dumps(parsed, ensure_ascii=False), json.dumps(changes, ensure_ascii=False),
                 json.dumps(evidence, ensure_ascii=False)))
            return cur.lastrowid
    except sqlite3.IntegrityError as error:
        raise ValueError("task id already exists for this project") from error
    finally:
        con.close()


def records(path, project=None, area=None):
    path = Path(path).expanduser()
    if not path.exists():
        return []
    terms, values = [], []
    for key, value in (("project", project), ("area", area)):
        if value is not None:
            terms.append(key + " = ?")
            values.append(value)
    clause = " WHERE " + " AND ".join(terms) if terms else ""
    con = connect(path)
    try:
        rows = [dict(row) for row in con.execute("SELECT * FROM tasks" + clause + " ORDER BY date,id", values)]
    finally:
        con.close()
    for row in rows:
        for key in ("causes", "changes", "evidence"):
            row[key] = json.loads(row[key])
    return rows


def summarize(rows):
    groups = defaultdict(list)
    for row in rows:
        groups[(row["project"], row["area"])].append(row)
    result = []
    for (project, area), tasks in sorted(groups.items()):
        kinds = Counter(c["kind"] for task in tasks for c in task["causes"])
        result.append({"project": project, "area": area, "tasks": len(tasks),
                       "mean_rounds": sum(task["rounds"] for task in tasks) / len(tasks),
                       "intent_returns": kinds["intent"], "causes": dict(sorted(kinds.items())),
                       "outcomes": dict(Counter(task["outcome"] for task in tasks))})
    return result


def change_windows(rows):
    result = []
    for row in rows:
        if not row["changes"]:
            continue
        same = [x for x in rows if (x["project"], x["area"]) == (row["project"], row["area"])]
        key = (row["date"], row["id"])
        before = [x["rounds"] for x in same if (x["date"], x["id"]) <= key]
        after = [x["rounds"] for x in same if (x["date"], x["id"]) > key]
        result.append({"project": row["project"], "area": row["area"], "task_id": row["task_id"],
                       "changes": row["changes"], "before_n": len(before), "after_n": len(after),
                       "before_mean": sum(before) / len(before),
                       "after_mean": sum(after) / len(after) if after else None})
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db", default=os.environ.get("AGENT_JOURNAL_DB") or
                        str(Path.home() / ".codex/agent-workflow/journal.sqlite"))
    sub = parser.add_subparsers(dest="command", required=True)
    add_parser = sub.add_parser("add")
    for key in ("project", "area", "task-id", "task"):
        add_parser.add_argument("--" + key, required=True)
    add_parser.add_argument("--rounds", type=int, required=True)
    for key in ("cause", "change", "evidence"):
        add_parser.add_argument("--" + key, action="append", default=[])
    add_parser.add_argument("--date")
    add_parser.add_argument("--outcome", choices=("accepted", "abandoned"), default="accepted")
    for command in ("list", "stats"):
        view = sub.add_parser(command)
        view.add_argument("--project")
        view.add_argument("--area")
    args = parser.parse_args(argv)
    try:
        if args.command == "add":
            result = {"id": add(args.db, project=args.project, area=args.area, task_id=args.task_id,
                                task=args.task, rounds=args.rounds, causes=args.cause,
                                changes=args.change, evidence=args.evidence, date=args.date,
                                outcome=args.outcome)}
        else:
            rows = records(args.db, args.project, args.area)
            result = rows if args.command == "list" else {
                "areas": summarize(rows), "changes": change_windows(rows),
                "note": "Observations only. Before includes the task that led to a change. No causal claim."}
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except (ValueError, OSError, sqlite3.Error) as error:
        print("journal: " + str(error), file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
