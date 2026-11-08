---
name: go-testing
description: Use when writing, reviewing, or running Go tests, or verifying Go changes across modules and services.
---

# Go testing

Read the project's test commands and dependency rules first. Identify affected modules, workspaces, build tags, generated files, and required services. Run tests and applicable static checks in each affected module; do not assume a root `go test ./...` covers every module.

## Unit tests

- Test observable non-trivial behavior, edge cases, and failure paths. Use table-driven tests when they make cases clearer.
- Follow the existing project's test conventions and dependencies. Do not add testify to an existing project solely for this skill.
- For a new project without an established test approach, use `github.com/stretchr/testify` if its dependency rules permit it. Choose a version compatible with the project's Go version and inspect `go.mod` and `go.sum` for unrelated upgrades.
- When using testify, use `assert` for independent checks and `require` when failure makes the rest of the test unsafe or meaningless. Call `require` from the goroutine running the test, not a worker.
- Keep tests deterministic: do not use sleeps for synchronization or real public network calls, and do not leave goroutines running after the test ends.

## Verification

- Check changed Go files with `gofmt -l`. Run project static checks and `go vet ./...` in affected modules when applicable.
- Test HTTP handlers with representative requests, invalid input, dependency failures, and cancellation where relevant. Run CLI or startup changes through the actual command.
- Use integration checks for real database, queue, or external-service behavior. Report unavailable services and checks that could not run.
- For shared state or goroutines, run `go test -race` on a supported platform. A passing run covers only executed paths.

## Reference

- [Testify assertions, mocks, and suites](references/testify.md): read when using or reviewing testify features.
