# Skill evaluations

`evals.json` defines behavioral scenarios, not executable tests. Each case contains a user `prompt`, the required test `setup`, an `expected_output` summary, and review `assertions`. IDs 1–35 cover library choice and compatibility, queries and scanning, database errors, transactions, pool lifecycle, monitoring, testing, and migrations.

To run a case manually:

1. Create a disposable project and, when needed, a disposable PostgreSQL instance matching its `setup`. Supply the candidate with the project and `prompt`, not the expected output or assertions. Use a fresh agent session with this skill available for each case.
2. Inspect the candidate's actual answer and changed files against every assertion. Run the generated project's relevant tests and PostgreSQL integration checks where applicable; report unavailable services as not tested.
3. Record pass or fail and evidence for each assertion, including test output and any limits. An assertion that cannot be verified is not a pass. For comparisons, repeat the same case and setup in a fresh session without the skill.

The cases specify the test context; they do not include ready-made Go projects, database fixtures, or an automated grader for every case. Model-based grading can be wrong and needs inspection. Valid JSON or a skill validator does not prove the scenarios pass.

## Run in the Codex app

Ask Codex in this repository, for example: `Run go-postgresql eval case 5 locally using my current Codex session.` To request the suite, replace `case 5` with `all cases`.

For each case, the evaluator should prepare the specified disposable context, give a fresh candidate session only the skill, setup, and prompt, then grade its actual result against the assertions. Run generated code and PostgreSQL integration tests when applicable. Record each assertion as pass, fail, or not verified with evidence; stop or report a missing test environment instead of treating it as a pass. Do not copy assertions or expected answers into the candidate prompt. Keep temporary projects and results outside Git.

Model usage counts against the current Codex account's plan and may use credits. Prepare the required fixtures before running each case.
