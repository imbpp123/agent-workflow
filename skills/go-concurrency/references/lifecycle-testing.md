# Goroutine lifecycle and testing

## Lifetime and errors

- Before starting a goroutine, define its owner, purpose, and exit conditions. Finite work may finish on its own. Long-lived work and work that can block need a shutdown path.
- Pass cancellation to work that should stop with its caller. Each blocking operation must handle cancellation or have another reliable way to unblock. Calling a cancel function does not wait for work to finish.
- The owner must wait for started work before releasing resources it uses. `sync.WaitGroup` waits for goroutines. It does not stop them or collect errors. Report errors to the owner when needed. Define whether one failure cancels other work.
- Limit concurrency when input or work can grow without a bound. Use workers, a semaphore, or an existing group helper. Choose a limit from available resources. Blocked producers must also be able to stop.

## Verification

Test normal completion, cancellation, dependency failure, and shutdown while blocked where relevant. Use explicit signals to control order. Use [go-testing](../../go-testing/SKILL.md) for general test design and check reporting.

For a worker that can block on a result send:

1. Use an unbuffered output channel with no receiver. Let the test observe when the worker reaches the send path.
2. Wait for that signal before canceling. A signal before a send shows the path was reached. It does not prove the exact moment the scheduler blocked the goroutine.
3. Cancel and wait for this worker's completion signal or join method. Keep the output without a receiver during this check, so a normal send cannot release it.
4. Bound test waits with timeouts as failure guards. Do not use sleeps to set the order. Arrange cleanup before a check can stop the test. Cleanup must cancel or release work and wait for it to exit. After a failed check, cleanup may receive from the output to release a broken worker.

Use the same approach for blocked receives or dependencies: control the blocking condition, cancel, and observe worker exit.

Run `go test -race` for affected packages on a supported platform. It reports races only in paths that ran. A passing run does not prove all paths are free of races. It also does not prove worker exit or the absence of goroutine leaks.

Use existing project leak checks or goroutine profiles to investigate leaks. A goroutine count alone does not prove a leak. Check lifetimes and stack traces. Do not add a dependency only because the code uses concurrency.
