# Synchronization

Choose the simplest mechanism that keeps the required state valid. A channel can coordinate or transfer work. A mutex is often simpler for shared state. Both still need clear ownership.

## Shared state

- Use `sync.Mutex` to protect related state and the rules it must follow. Make clear which state the lock protects. Hold a lock over slow work only when correctness requires it.
- Use `sync.RWMutex` when concurrent reads help. Do not take a write lock while holding a read lock. Release the read lock first. Recheck state after taking the write lock. Measure before claiming a performance gain.
- Use `sync/atomic` for independent values, such as a counter or flag. Atomic updates to separate fields do not make a group of updates atomic.
- Prefer a typed map with a mutex when map operations must keep related state valid. `sync.Map` fits entries written once and read many times, or callers that use separate key sets. Check that this fits the work.
- Do not copy a mutex, `sync.Map`, `sync.WaitGroup`, or other synchronization value after first use. This includes copies of a struct that holds it. Use a pointer when a receiver, argument, or assignment would copy a used value.

## Waiting and grouped work

Use `sync.WaitGroup` to wait for tasks. It does not cancel them or collect errors. With `Add` and `Done`, register each task before starting its goroutine. This keeps `Wait` from returning early:

```go
wg.Add(1)
go func() {
	defer wg.Done()
	work()
}()
wg.Wait()
```

`WaitGroup.Go` requires Go 1.25 or later. Use it only if the project's Go version supports it. Its function must not panic.

Consider `golang.org/x/sync/errgroup` for errors and optional cancellation of other tasks. Add it only when the dependency is justified. `WithContext` cancels the derived context on the first error or when `Wait` returns. Tasks still need to handle cancellation. `SetLimit` limits active tasks and can block `Go`. A blocked call to `Go` must not prevent running tasks from finishing.

## One-time work and reuse

- Use `sync.Once` for initialization that should run once. It does not retry a failed or panicking function. Use another design when retries are required.
- Use `singleflight` when concurrent calls for the same key should share one result from active work. It is not a cache. Add the dependency only when useful.
- Use `sync.Pool` for temporary objects only when profiling supports reuse. The runtime may discard pooled values at any time. Reset objects as needed before reuse. Do not use them after returning them to the pool.
