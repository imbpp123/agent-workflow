# Skill evaluations

`evals.json` contains behavior checks, not executable tests. Each case has a user `prompt`, required `setup`, `expected_output`, and review `assertions`. IDs 1–35 cover database libraries, queries, errors, transactions, pools, monitoring, tests, and migrations. IDs 36–37 cover new UUID identifiers and existing ID contracts. ID 38 checks repository names, atomic writes, and hidden driver types with `go-code-style` and `go-clean-architecture`.

An optional `additional_skills` list names the other skill folders needed for a case. Supply this skill and every listed skill, including their relevant references. Do not depend on automatic skill selection.

To run a case manually:

1. Create a disposable project and PostgreSQL instance when the `setup` needs them. Give a fresh candidate session the setup, prompt, this skill, and any `additional_skills`. Keep expected output and assertions out of its prompt.
2. Compare the actual answer and changed files with every assertion. Run relevant project tests and PostgreSQL checks for code changes. For a design-only case, review the concrete design and report that no runtime check ran.
3. Record pass, fail, or not verified for each assertion, with evidence and limits. Missing services and unchecked assertions are not passes. For a comparison, repeat the setup in a fresh session without the skill. State which additional skills, if any, remain in the comparison.

The cases define the context. They do not include full Go projects, database fixtures, or a general runner. Inspect model grading; it can be wrong. Valid JSON and skill validation do not prove these cases pass.

## Run in the Codex app

Ask Codex in this repository, for example: `Run go-postgresql eval case 5 locally using my current Codex session.` To request the suite, replace `case 5` with `all cases`.

For each case, prepare the disposable setup. Give a fresh candidate only the setup, prompt, this skill, and any `additional_skills`. Review its actual result against the assertions. Run generated code and PostgreSQL checks when needed. Record evidence and missing checks. Do not copy expected answers or assertions into the candidate prompt. Keep temporary projects and results outside Git.

Model usage counts against the current Codex account's plan and may use credits. Prepare the required fixtures before running each case.
