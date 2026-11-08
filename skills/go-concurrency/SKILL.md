---
name: go-concurrency
description: Use when writing, reviewing, or debugging concurrent Go code involving goroutines, channels, synchronization, shared state, or cancellation.
---

# Go concurrency

Follow the project's Go version, conventions, and dependencies. Use concurrency when it serves the task; keep ownership and synchronization clear.

- Give each goroutine a clear owner, exit condition, and way to observe completion when needed. Arrange cancellation and error propagation where the operation requires them.
- Protect shared mutable state or transfer ownership explicitly. Choose channels, locks, or atomics based on the invariant, not a blanket preference.
- Bound concurrency when workload or resources require it. Ensure blocked operations can finish or be canceled when their caller stops waiting.
- Test concurrent behavior and shutdown deterministically. Run `go test -race` for affected packages on a supported platform; it only detects races on executed paths.

## References

- [Goroutine lifecycle and testing](references/lifecycle-testing.md): startup, shutdown, errors, limits, and tests.
- [Channels and pipelines](references/channels.md): communication, ownership, closing, buffering, and cancellation.
- [Synchronization](references/synchronization.md): locks, wait groups, atomics, concurrent maps, and coordination helpers.
