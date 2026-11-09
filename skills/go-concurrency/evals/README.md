# Go concurrency evaluations

`evals.json` has behavior cases for goroutine lifetime, cancellation, bounded work, channels, synchronization, and shutdown tests. These cases are not executable tests or prepared Go projects. Valid JSON does not prove that an agent follows the skill.

A case may list `additional_skills`. Give the fresh candidate those skills and their relevant references along with this skill. Keep the task and constraints unchanged. Case 7 combines `go-concurrency` and `go-testing` to check a blocked worker's shutdown.

To run a case in the Codex app, ask: `Run go-concurrency eval case 1 locally using my current Codex session. Do not use an API key or GitHub Actions.` Replace the case number or request all cases.

For each case:

1. Prepare a disposable project matching `setup`. Give a fresh candidate the task, setup, this skill, and any `additional_skills`, with their relevant references. Do not give the candidate `expected_output` or `assertions`. For a baseline, use a separate equivalent project and fresh candidate without the skills under test.
2. Check the candidate's changes and answer against every assertion. For implementation or test changes, run relevant Go tests and `go test -race` on a supported platform. Control dependencies and bound waits to test cancellation, failures, and shutdown. A design sketch is enough only for a case that asks for design. Review its declarations and call sites; do not report it as executed code.
3. Record pass, fail, or not verified for each assertion with evidence. Missing tools, unsupported race detection, and unrun checks are not passes. The race detector does not prove worker exit; see the [lifecycle testing reference](../references/lifecycle-testing.md) for its limits. Accept other implementations that meet the contract.

The evaluator creates the projects and tests. Use a fresh candidate for each case. Keep generated files and results outside Git. Model usage may count against the account's plan.
