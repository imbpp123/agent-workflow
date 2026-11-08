# Go code style evaluations

`evals.json` contains behavioral scenarios for `go-code-style`. Each case gives a candidate prompt and setup, plus an expected outcome and assertions for the evaluator. The cases cover project conventions, naming, API boundaries, errors and resources, values and declarations, control flow, layout, and strings and conversions.

These are scenario descriptions, not executable tests or prepared Go fixtures. A valid JSON file or a skill validator does not show that a model follows the skill.

## Run a case in the Codex app

Ask Codex in this repository: `Run go-code-style eval case 1 locally using my current Codex session. Do not use an API key or GitHub Actions.` Replace the case number or request all cases as needed.

For each case:

1. Prepare a disposable Go project outside Git using the setup. Supply a fresh candidate with the task, setup, and this skill, including its references. Do not supply `expected_output` or `assertions` to the candidate. Use a fresh candidate and project for a baseline without the skill if comparing results.
2. Inspect the candidate's output and actual changes against each assertion. Check relevant behavior with executable Go tests, including failure paths, and run `gofmt` checks. Verify version-sensitive cases using the requested Go version or a matching module language version, and follow the case's project constraints.
3. Record pass, fail, or not verified for each assertion with evidence. Report missing tools or environments instead of counting them as passes. A valid alternative is acceptable when it satisfies the contract; do not require a particular spelling or code shape unless the case requires it.

The evaluator must construct the disposable projects and tests. Running all cases requires separate candidate sessions; results and generated files stay outside Git. Model usage may count against the account's plan. There is no automated runner or API-key workflow for these cases.
