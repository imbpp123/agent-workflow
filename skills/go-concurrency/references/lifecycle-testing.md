# Goroutine lifecycle and testing

## Lifetime and errors

- Before starting a goroutine, identify its owner, purpose, and exit conditions. A finite operation may finish on its own; long-lived or potentially blocked work needs a shutdown path.
- Propagate cancellation where work should stop with its caller. Cancellation is cooperative: every blocking operation must either support cancellation or have another reliable way to unblock. Calling a cancel function does not wait for work to finish.
- Arrange for the owner to wait for started work before releasing resources it uses. `sync.WaitGroup` waits but does not stop goroutines or collect errors. When needed, report errors to an owner and define whether one failure cancels other work.
- Bound concurrency when the input or workload can grow without limit, using workers, a semaphore, or an existing group abstraction. Choose the limit from resource constraints; ensure blocked producers can also stop.

## Verification

- Test normal completion, cancellation, dependency failure, and shutdown while blocked where they matter. Use channels, barriers, controlled dependencies, and bounded waits to coordinate tests; do not use sleeps to establish ordering. Clean up and wait for goroutines started by tests.
- Run `go test -race` for affected packages on a supported platform. The race detector only reports races in executed paths; a passing run does not prove the absence of races or goroutine leaks.
- Use existing project leak checks or goroutine profiles when investigating suspected leaks. A goroutine count alone is not proof of a leak; inspect lifetime and stack traces. Avoid adding a dependency solely because concurrency is present.
