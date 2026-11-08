# Go concurrency evaluations

`evals.json` contains behavioral scenarios for goroutine lifetime, cancellation, bounded work, channels, synchronization, and deterministic tests. These are scenarios, not executable tests or prepared Go projects. A valid file does not prove that an agent follows the skill.

To run a case in the Codex app, ask: `Run go-concurrency eval case 1 locally using my current Codex session. Do not use an API key or GitHub Actions.` Replace the case number or request all cases.

For each case:

1. Prepare a disposable project matching `setup`. Give a fresh candidate the task, setup, and skill including its references, but not `expected_output` or `assertions`. For a baseline comparison, use a separate project and candidate without the skill.
2. Inspect the candidate's changes and answer against every assertion. Run relevant Go tests and `go test -race` on a supported platform. Use controlled dependencies and bounded waits to exercise cancellation, failures, and shutdown. A passing race detector only covers executed paths and does not prove absence of leaks.
3. Record pass, fail, or not verified for each assertion with evidence. Missing tools, unsupported race detection, and unrun checks are not passes. Accept alternative implementations that satisfy the contract.

The evaluator creates the projects and tests. Keep generated artifacts and results outside Git. Model usage may count against the account's plan.
