---
name: go-checks
description: Verify changes in Go applications using project commands, formatting, unit tests, go vet, and race checks when concurrency changes. Use for Go source, modules, workspaces, HTTP handlers, services, and command line applications.
---

# Verify Go applications

Read project commands first. Locate the affected `go.mod` files, `go.work`, Go version, build tags, generated files, and service requirements. Do not assume `go test ./...` at the repository root covers a workspace with multiple modules.

| Change | Check |
| --- | --- |
| Go source | Check formatting of changed Go files with `gofmt -l`; format only intended files. |
| Non-trivial behavior | Unit tests for success, edge cases, and errors. Use project test commands or `go test ./...` in each affected module. |
| Go code | Run project static checks, including `go vet ./...` in affected modules when applicable. |
| Shared state, goroutines, locks, channels | Run `go test -race ./...` for affected modules on a supported platform. A passing race run covers only executed paths. |
| HTTP handler | Exercise method, status, body, invalid input, dependency failures, and cancellation where relevant. Prefer `httptest` and bounded local tests. |
| CLI or startup wiring | Run the actual built command with controlled input and check its exit status and output. |
| Database, queue, external service | Run the existing integration check with its required services. State explicitly if those services are unavailable. |
| Dependency change | Explain why it is needed; inspect `go.mod` and `go.sum`. Use the project's Go version. Do not upgrade unrelated modules. |

Keep tests deterministic. Avoid sleeps as synchronization, real public network calls, and background goroutines that outlive a test. Use contexts, cleanup, controlled clocks when needed, and temporary directories. Preserve error chains when behavior relies on `errors.Is` or `errors.As`.

Do not add interfaces solely for mocking trivial code. Place real side effects at boundaries that tests can control. Do not refactor unrelated code to satisfy a test.

If checks fail because of an existing defect, missing toolchain, network, build tag, or missing service, report the exact boundary. Do not silently replace an integration check with a unit test.
