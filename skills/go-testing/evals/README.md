# Go testing evaluations

`evals.json` has behavior cases for Go unit and integration tests, checks across modules, and Testify assertions, mocks, and suites. These cases are not executable tests or prepared projects. Valid JSON does not prove that an agent follows the skill.

A case may list `additional_skills`. Give the fresh candidate those skills and their relevant references along with this skill. Keep the task and constraints unchanged. The combined blocked-worker case is case 7 in [go-concurrency evaluations](../../go-concurrency/evals/evals.json); it also loads `go-testing`.

To run a case in the Codex app, ask: `Run go-testing eval case 1 locally using my current Codex session. Do not use an API key or GitHub Actions.` Replace the case number or request all cases.

For each case:

1. Prepare a disposable project matching `setup`. Give a fresh candidate the project, task, this skill, and any `additional_skills`, with their relevant references. Do not give the candidate `expected_output` or `assertions`. For a baseline, use a separate equivalent project and fresh candidate without the skills under test.
2. Check the candidate's changes and answer against every assertion. For implementation or test changes, run relevant tests and checks through the real entry point. Use controlled dependencies and a real test service when the case needs one. A design sketch is enough only for a case that asks for design. Review its declarations and call sites; do not report it as executed code. Accept other implementations that meet the contract.
3. Record pass, fail, or not verified for each assertion with evidence. Missing tools, unavailable services, and unrun checks are not passes. For race detector limits and worker shutdown checks, see the [lifecycle testing reference](../../go-concurrency/references/lifecycle-testing.md).

The evaluator creates the projects and fixtures. Use a fresh candidate for each case. Keep generated files and results outside Git. Model usage may count against the account's plan.
