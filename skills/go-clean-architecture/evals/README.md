# Go Clean Architecture evaluations

`evals.json` contains nine scenarios. Each case has a task, setup, expected result, and checks. Prepare a Go project before running a case. A valid JSON file alone does not show that the skill works.

| Case | Main checks |
| --- | --- |
| 1 | Shared domain rules for HTTP and CLI. Safe cancellation during concurrent shipping. |
| 2 | Domain pricing rules and an external service port. |
| 3 | One transaction for an order and its audit record. |
| 4 | Payment retries after an uncertain result. |
| 5 | Missing data, technical errors, and public responses. |
| 6 | A focused refactor with manual dependency wiring and no DI framework. |
| 7 | An interface owned by the handler. Direct use of allowed types and pure functions. |
| 8 | SQL types and row handling inside the storage adapter. |
| 9 | A small fix in a project without Clean Architecture. |

To run a case in the Codex app, ask: `Run go-clean-architecture eval case 1 locally using my current Codex session. Do not use an API key or GitHub Actions.` Replace the case number or request all cases.

For each case:

1. Prepare a disposable project matching `setup`. Give a fresh candidate the task, setup, and skill, but not `expected_output` or `assertions`. For a baseline comparison, use a separate project and candidate without the skill.
2. Inspect the candidate's changes and answer against each assertion. Run relevant Go tests and integration checks when applicable. Check actual import direction and failure behavior rather than package names alone.
3. Record pass, fail, or not verified for each assertion with evidence. Missing tools, services, and unrun integration tests are not passes. Accept alternative implementations that satisfy the contract.

Keep the candidate prompt limited to the task, setup, and skill. Do not add architecture hints or dependency limits that are absent from the case. Cases 6 and 7 leave dependency choices open so the skill's DI rule can be checked. For case 9, keep the original task wording so the skill's scope rule can be checked.

The evaluator prepares the disposable workspaces and any required fixtures, and independently checks the results. Keep generated artifacts and results outside Git. Model usage may count against the account's plan.
