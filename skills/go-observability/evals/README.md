# Go observability evaluations

`evals.json` describes behavioral scenarios for logging, retries, error boundaries, metrics, tracing, lifecycle events, and verification limits. These are scenarios, not executable tests or prepared Go projects. Valid JSON does not prove that an agent follows the skill.

To run a case in the Codex app, ask: `Run go-observability eval case 1 locally using my current Codex session. Do not use an API key or GitHub Actions.` Replace the number or request all cases.

For each case:

1. Prepare a disposable project matching `setup`. Give a fresh candidate the prompt, setup, and skill, without `expected_output` or `assertions`. For comparison, use a separate project and candidate without the skill.
2. Inspect the candidate's actual changes and answer against every assertion. Run relevant Go tests and check recorded signals, sensitive data, and context propagation where applicable. Accept alternative implementations that satisfy the contract.
3. Record pass, fail, or not verified for each assertion with evidence. Missing services or unrun checks are not passes; unit tests do not prove live exporter delivery.

The evaluator creates the projects and tests. Keep generated artifacts and results outside Git. Separate candidate sessions are required; model usage may count against the account's plan. There is no automated runner for these cases.
