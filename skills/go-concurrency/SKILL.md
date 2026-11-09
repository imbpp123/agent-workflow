---
name: go-concurrency
description: Use when writing, reviewing, or debugging concurrent Go code involving goroutines, channels, synchronization, shared state, or cancellation.
---

# Go concurrency

Follow the project's Go version, conventions, and dependencies. Use concurrency when the task needs it. Keep ownership and synchronization clear.

- Give each goroutine an owner and an exit condition. Let the owner observe completion when needed. Define how cancellation and errors reach other work.
- Protect shared mutable state or transfer ownership clearly. Choose channels, locks, or atomics to keep the required state valid.
- Limit concurrency when work or resources need a bound. A blocked operation must finish or support cancellation when its caller stops waiting.
- Test concurrent behavior and prove worker shutdown. Use explicit signals and wait for started workers. Run `go test -race` for affected packages on a supported platform. It covers only paths that run.

This skill covers lifetime, ownership, cancellation, blocking, and synchronization. Use [go-testing](../go-testing/SKILL.md) for general test design, fakes, mocks, and check reporting.

## References

- [Goroutine lifecycle and testing](references/lifecycle-testing.md): startup, shutdown, errors, limits, and tests.
- [Channels and pipelines](references/channels.md): communication, ownership, closing, buffering, and cancellation.
- [Synchronization](references/synchronization.md): locks, wait groups, atomics, concurrent maps, and coordination helpers.
