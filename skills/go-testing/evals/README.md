# Go testing evaluations

`evals.json` contains behavioral scenarios for Go unit and integration tests, verification across modules, and testify assertions, mocks, and suites. The scenarios are not executable tests or prepared projects. Valid JSON does not prove that an agent follows the skill.

To run a case in the Codex app, ask: `Run go-testing eval case 1 locally using my current Codex session. Do not use an API key or GitHub Actions.` Replace the case number or request all cases.

For each case:

1. Prepare a disposable project matching `setup`. Give a fresh candidate the project, task, and skill with its references, but not `expected_output` or `assertions`. For a baseline comparison, use a separate equivalent project and fresh candidate without the skill.
2. Inspect the candidate's changes and answer against every assertion. Run relevant generated tests and checks through the real entry point. Use controlled dependencies and a real test service when an integration case requires one. Accept alternative implementations that satisfy the contract.
3. Record pass, fail, or not verified for each assertion with evidence. Missing tools, unavailable services, and unrun checks are not passes. A race detector covers only executed paths; it does not prove the absence of races or leaks.

The evaluator creates the projects and fixtures. Keep generated artifacts and results outside Git. Model usage may count against the account's plan.
