# Synchronization

Choose the simplest mechanism that preserves the invariant. A channel is useful for coordination or transferring work; a mutex is often simpler for shared state. Neither removes the need to define ownership.

## Shared state

- Use `sync.Mutex` to protect related state and its invariants. Keep the protected scope clear; avoid holding a lock over slow operations unless correctness requires it.
- Use `sync.RWMutex` when concurrent reads are useful. Do not upgrade a read lock to a write lock; release the read lock and recheck state after acquiring the write lock. Measure before assuming it improves performance.
- Use `sync/atomic` for suitable independent values, such as a counter or flag. Atomics on separate fields do not make a multi-field invariant atomic.
- Prefer a typed map with a mutex when map operations must preserve related invariants. `sync.Map` is specialized for write-once/read-many entries or disjoint key sets; use it when its behavior fits the workload.
- Do not copy a mutex, `sync.Map`, `sync.WaitGroup`, or other synchronization value after first use.

## Waiting and grouped work

Use `sync.WaitGroup` to wait for tasks; it does not cancel them or collect errors. When using `Add` and `Done`, register each task before starting its goroutine so `Wait` cannot return early:

```go
wg.Add(1)
go func() {
	defer wg.Done()
	work()
}()
wg.Wait()
```

Go 1.25 introduced `WaitGroup.Go`; use it only when supported by the project's Go version. Its function must not panic. For errors and optional sibling cancellation, consider `golang.org/x/sync/errgroup` if the dependency is justified. `WithContext` cancels its derived context on the first error or when `Wait` returns; tasks must cooperate with cancellation. `SetLimit` limits active tasks and can block `Go`, so avoid designs where blocked submission prevents running tasks from finishing.

## One-time work and reuse

- Use `sync.Once` for initialization that should run once. A failed or panicking function is not automatically retried; choose another design if retries are required.
- Use `singleflight` only when concurrent calls for the same key should share one in-flight result. It is not a cache; add the dependency only when useful.
- Use `sync.Pool` for temporary reusable objects only when profiling justifies it. The runtime may discard pooled values at any time. Reset objects as needed before reuse and do not use them after returning them to the pool.
