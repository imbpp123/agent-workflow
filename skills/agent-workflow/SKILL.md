---
name: agent-workflow
description: Deliver a coding task with explicit acceptance criteria, verification through the real user entry point, and evidence. Use for application changes and recurring delivery failures; use retro after accepted substantial work.
---

# Task delivery

1. Read project AGENTS.md, README, CONTRIBUTING, and linked documents relevant to the task. Inspect Git state before changes; preserve other work.
2. State the expected behavior and a way to check it. Use a reasonable stated assumption when possible. Ask only when intent or a missing decision blocks useful work.
3. Choose technical details yourself. For taste or ambiguous product behavior, show a small preview or options with a recommendation before building the full result.
4. Make the smallest sufficient change. Cover non-trivial logic with deterministic unit tests, including edge and failure cases.
5. Verify through the entry point used by the user: the actual command, route, binary, or UI. A fixture that constructs a correct result cannot prove that the shipped path creates it. Unit tests and integration checks serve different purposes.
6. Report changed behavior, files, checks, and remaining limits. If an environment or service is missing, distinguish what ran from what remains unverified. Do not call an untested scenario fixed.

Use relevant specialist skills for the language and work when available.
For risky architecture decisions, request a fresh review when available and authorized: provide the problem and source, not your conclusion. Treat findings as hypotheses and verify them.

# After acceptance

Use `retro` when the user accepts or abandons a substantial task: a return, a pipeline change, or an unexpected result. Keep the report short. Do not interrupt active work to demand a retro.

Repeated failures should lead to a narrow tested change in the existing mechanism before a new rule. Record successful approaches only when they are reusable and not already documented.

# Durable knowledge

- Keep project commands and conventions in that project's guidance. Shared skills must stand without project names or private paths.
- Treat memory as a claim: check source, Git, actual runtime, or external state as appropriate before relying on it.
- Remove accepted temporary state notes only after the facts are preserved in Git or maintained docs.
- Keep a small memory index; move tested reusable lessons into skills.
- Do not automatically update shared code, commit, push, publish, or send messages during a retro. Follow the user's existing authorization.
