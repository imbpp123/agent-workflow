---
name: go-testing
description: Use when writing, reviewing, or running Go tests, or verifying Go changes across modules and services.
---

# Go testing

Read the project's test commands and dependency rules first. Find affected modules, workspaces, build tags, generated files, and required services. Run tests and relevant static checks in each affected module. A root `go test ./...` may not cover every module.

This skill covers test design, fakes, mocks, Testify, check commands, and reporting. Use [go-concurrency](../go-concurrency/SKILL.md) for goroutine ownership, cancellation, and tests that prove worker shutdown.

## Unit tests

- Test observable non-trivial behavior, edge cases, and failure paths. Use table-driven tests when they make cases clearer.
- Prefer a simple fake or stub when only the result matters. Use mock expectations when the interaction is part of the contract.
- Follow the existing project's test style and dependencies. Do not add Testify to an existing project only for this skill.
- For a new project with no test approach, use `github.com/stretchr/testify` if dependency rules allow it. Choose a version that supports the project's Go version. Check `go.mod` and `go.sum` for unrelated upgrades.
- With Testify, use `assert` for independent checks. Use `require` when failure makes later checks unsafe or meaningless. Call `require` from the test goroutine, not a worker.
- Keep tests deterministic. Use controlled dependencies and explicit signals instead of public network calls or sleeps for ordering. Use timeouts to bound waits. Clean up and wait for goroutines started by the test, including after a failed check.

## Verification

- Check changed Go files with `gofmt -l`. Run project static checks and `go vet ./...` in affected modules when applicable.
- Test HTTP handlers with normal requests, invalid input, dependency failures, and cancellation where relevant. Run CLI or startup changes through the actual command.
- Use integration checks for real database, queue, or external-service behavior. Report commands that ran, their results, and checks that could not run. Give the reason for each missing check.
- For shared state or goroutines, run `go test -race` on a supported platform. See [lifecycle testing](../go-concurrency/references/lifecycle-testing.md) for its coverage limits and shutdown checks.

## Reference

- [Testify assertions, mocks, and suites](references/testify.md): read when using or reviewing testify features.
