# Go Clean Architecture evaluations

`evals.json` contains six behavioral scenarios for domain and application services, dependencies and adapters, transactions, external effects, and error boundaries. These are scenarios, not executable tests or prepared Go projects. A valid file does not prove that an agent follows the skill.

To run a case in the Codex app, ask: `Run go-clean-architecture eval case 1 locally using my current Codex session. Do not use an API key or GitHub Actions.` Replace the case number or request all cases.

For each case:

1. Prepare a disposable project matching `setup`. Give a fresh candidate the task, setup, and skill, but not `expected_output` or `assertions`. For a baseline comparison, use a separate project and candidate without the skill.
2. Inspect the candidate's changes and answer against each assertion. Run relevant Go tests and integration checks when applicable. Check actual import direction and failure behavior rather than package names alone.
3. Record pass, fail, or not verified for each assertion with evidence. Missing tools, services, and unrun integration tests are not passes. Accept alternative implementations that satisfy the contract.

The evaluator prepares the disposable workspaces and any required fixtures, and independently checks the results. Keep generated artifacts and results outside Git. Model usage may count against the account's plan.
