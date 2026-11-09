# Go code style evaluations

`evals.json` contains behavioral scenarios for `go-code-style`. Each case gives a candidate prompt and setup, plus an expected outcome and assertions for the evaluator. The cases cover project conventions, naming, repositories, API boundaries, errors and resources, values and declarations, control flow, layout, and strings and conversions.

These are scenario descriptions, not executable tests or prepared Go fixtures. A valid JSON file or a skill validator does not show that a model follows the skill.

A case may list `additional_skills`. Supply those skills and their relevant references together with this skill. Keep the case's task and constraints the same when checking their combined effect.

## Run a case in the Codex app

Ask Codex in this repository: `Run go-code-style eval case 1 locally using my current Codex session. Do not use an API key or GitHub Actions.` Replace the case number or request all cases as needed.

For each case:

1. Prepare the case from its setup. Use a disposable Go project outside Git when the case needs files. Supply a fresh candidate with the task, setup, and this skill, including its references. Do not supply `expected_output` or `assertions` to the candidate. Use a fresh candidate and setup for a baseline without the skill if comparing results.
2. Inspect the candidate's output and actual changes against each assertion. For code changes, check behavior with Go tests, including failure paths, and run `gofmt` checks. For design sketches, review the declarations and call sites. Check version-sensitive cases with the requested Go version or a matching module language version. Follow the case's project constraints.
3. Record pass, fail, or not verified for each assertion with evidence. Report missing tools or environments instead of counting them as passes. A valid alternative is acceptable when it satisfies the contract; do not require a particular spelling or code shape unless the case requires it.

The evaluator prepares the projects and tests each case needs. Use a separate candidate session for each case. Keep results and generated files outside Git. Model usage may count against the account's plan. There is no automated runner or API-key workflow for these cases.
