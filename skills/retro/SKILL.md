---
name: retro
description: Review an accepted or abandoned coding task, count returns and their causes, record tested workflow improvements and successful practices in a local journal. Use when asked for a retro or after substantial work is accepted.
---

# Retro

Read `../agent-workflow/SKILL.md` if it was not included in context. Locate the shared repo by resolving this skill directory; the journal is `../../scripts/journal.py` relative to this directory.

1. Confirm what was accepted or abandoned from the conversation and source state. Do not invent acceptance, a return, or a cause.
2. Count each human return once and record its plain reason. Separate changes in intent from defects. Use one class per return: `verification`, `knowledge`, `scope`, `intent`, `tooling`, `collision`.
3. Find the existing skill, test, rule, or tool that should have prevented a repeated defect. Correct that mechanism and test the relevant behavior. Add a new rule only for a supported reusable gap. A return caused by changed intent may need an earlier preview, not another technical prohibition.
4. Record a concrete change and evidence of its check. If work is blocked, report the unfinished retro; do not add a completed journal entry with imaginary changes. Keep a successful reusable practice when it adds knowledge.
5. Put project facts in project docs and portable lessons in shared skills without private identifiers. Remove stale memory only after facts are preserved. Do not automatically commit, push, or publish.
6. Write one journal record per task with a stable task id, project, area, return count, causes, changes, and evidence. Use a real issue id or another stable local id. Repeating a retro must not add another record for the same task.

```sh
python3 /path/to/agent-workflow/scripts/journal.py add \
  --project service --area http --task-id issue-42 --task 'Request timeout' \
  --rounds 1 --cause 'verification:Cancellation was not checked' \
  --change 'Added a cancellation test' --evidence 'test or commit reference'
```

Use `--rounds 0` without causes for first-pass acceptance. `--outcome abandoned` records abandoned work; count existing returns honestly. Journal content stays local.

Report in Russian, a few lines: returns; main cause; what changed and how checked; any unresolved work. Statistics are observations with sample counts, not proof that a skill caused improvement.
