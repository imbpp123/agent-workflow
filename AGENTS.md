# Agent Workflow

Read README.md before changing this repository.

- Keep chat replies brief and in Russian.
- Write all project text in B1-level English, including code comments, docs, skills, prompts, and commit messages. Use short, simple sentences. Get to the point. Keep the context, conditions, and exceptions that readers need.
- Keep the shared workflow independent of a project and language.
- Go is the first supported application stack. Do not add Unreal Engine content.
- Use Python 3.9+ standard library for local workflow tools. Do not add dependencies without a reason.
- Cover non-trivial behavior, invalid input, and failure paths with unit tests.
- Run `python3 -m unittest discover -s tests -v` before delivery.
- Validate changed skills with the bundled skill-creator validator when available.
- Keep runtime data, personal paths, and secrets out of Git.
- Do not change global Codex settings as a side effect of editing this repo.
- Do not commit or push unless the user asks. A retro does not imply publication.
- Before making changes, state the expected behavior and how to check it.
- Verify the change through the command, route, binary, or UI that users actually use.
- Report what changed, which checks ran, and what remains unverified.
- Do not claim a live hook test from a unit test.

Use `skills/agent-workflow/SKILL.md` for task delivery and `skills/retro/SKILL.md` after acceptance.
