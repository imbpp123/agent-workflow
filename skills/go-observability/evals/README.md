# Go observability evaluations

`evals.json` describes scenarios for logging, retries, errors, metrics, tracing, lifecycle events, scope, and verification limits. Each case gives a task, setup, expected result, and assertions. A valid JSON file does not prove that an agent follows the skill.

A case may list `additional_skills`. Supply those skills and their relevant references together with this skill. Case 3 checks error wrapping and safe reporting together. Case 9 checks the scope of a naming change.

To run a case in the Codex app, ask: `Run go-observability eval case 1 locally using my current Codex session. Do not use an API key or GitHub Actions.` Replace the number or request all cases.

For each case:

1. Prepare the case from its setup. Use a disposable project when the case needs files. Give a fresh candidate the prompt, setup, and skills. Keep `expected_output` and `assertions` for the evaluator. For comparison, use a separate project and candidate without the skills.
2. Inspect the candidate's changes and answer against every assertion. For code changes, run Go tests and check signals, sensitive data, and context where needed. For design sketches, review the declarations and call sites. Accept other implementations that satisfy the contract.
3. Record pass, fail, or not verified for each assertion with evidence. Missing services and unrun checks are not passes. Unit tests do not prove live exporter delivery.

The evaluator prepares the projects and tests each case needs. Keep generated files and results outside Git. Use a fresh candidate session for each case. Model usage may count against the account's plan. There is no automated runner for these cases.
