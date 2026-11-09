# Agent Workflow

Shared Codex skills and local tools for software delivery and retros. The workflow is language-independent; additional skills cover Go. Local tools require Python 3.9+ and use the standard library.

## Skills

- `agent-workflow` — task delivery and verification through the real entry point.
- `go-clean-architecture` — Go architecture and dependency boundaries.
- `go-code-style` — Go code style and readability.
- `go-concurrency` — goroutines, synchronization, channels, and tests.
- `go-observability` — logging, metrics, and tracing.
- `go-postgresql` — PostgreSQL access from Go.
- `go-testing` — Go tests and verification.
- `retro` — review accepted or abandoned work and record evidence.

## Install

On macOS or Linux, preview and then apply the installation:

```sh
python3 scripts/install.py --project /path/to/project
python3 scripts/install.py --project /path/to/project --apply
```

Use `--global` instead of `--project /path/to/project` for the current user. The installer links all skills under `.agents/skills` and refuses to replace existing skills. The target directory must exist. Automatic installation on Windows is not supported.

Start a new Codex session after installation. Codex can select skills by description, or you can invoke one explicitly, for example `$go-concurrency` or `$retro`. Automatic selection and compliance are not guaranteed. The links point to the source skills, so edits to `SKILL.md` are available in new sessions without reinstalling.

## Project rules

Add these rules to the project's `AGENTS.md`, along with its commands and constraints:

```markdown
- Before making changes, state the expected behavior and how to check it.
- Verify the change through the command, route, binary, or UI that users actually use.
- Report what changed, which checks ran, and what remains unverified.
```

## Optional hooks

Add `--with-hooks` to the install command to add `SessionStart` and `UserPromptSubmit` handlers to `.codex/hooks.json`. The installer preserves existing handlers and refuses conflicts. Avoid enabling the hooks both globally and locally. Approve them in Codex Settings → Hooks and verify context delivery in a new session. Installed files alone do not prove that a hook ran.

The default install leaves existing hook settings alone. To switch an older install to skills only, disable the Agent Workflow handlers in Codex Settings → Hooks, or remove only the handlers with the `Agent Workflow: load shared skills` status message from the matching project or user `hooks.json`.

With hooks enabled, you can select extra skills in `.agent-workflow.json`:

```json
{
  "always": ["go-code-style", "go-clean-architecture"],
  "routes": {"go-postgresql": ["postgresql", "postgres"]}
}
```

The hook always loads `agent-workflow`, plus skills in `always` and routes matching the prompt. Routes match case-insensitive word prefixes. It does not detect Go projects or apply built-in routes. Skills must exist in this repository; invalid configuration or more than 24,000 bytes of selected context prevents delivery.

The hook searches from the working directory up to the Git boundary. At the same directory, `.agent-workflow.local.json` takes precedence over `.agent-workflow.json`.

Replace old `go-coding` and `go-architecture` configuration entries with current skill names. The installer does not remove old links.

## Journal and retro

Use `$retro` after substantial work is accepted or abandoned. `scripts/journal.py` stores local records in `~/.codex/agent-workflow/journal.sqlite` by default; use `AGENT_JOURNAL_DB` or `--db` to override it. Keep journal data out of Git.

```sh
python3 scripts/journal.py --db /path/to/journal.sqlite add \
  --project api --area http --task-id issue-42 --task 'Handle request timeout' \
  --rounds 1 --cause 'verification:Timeout path was not tested' \
  --change 'Added a handler timeout test' --evidence 'test or commit reference'
python3 scripts/journal.py --db /path/to/journal.sqlite list --project api
python3 scripts/journal.py --db /path/to/journal.sqlite stats --project api
```

Record one cause per return. Cause classes are `verification`, `knowledge`, `scope`, `intent`, `tooling`, and `collision`. Statistics are observations, not proof of causation; evidence references are not checked automatically.

## Development

```sh
python3 -m unittest discover -s tests -v
```

Tests use temporary directories and do not verify live hook delivery in Codex. Skill evaluation instructions are in each Go skill's `evals/README.md`.
