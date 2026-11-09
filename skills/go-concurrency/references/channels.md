# Channels and pipelines

## Channel ownership

- Use channels when they make communication, ownership, and flow clear. Choose a mutex for shared state when it is simpler.
- Define who sends, receives, and closes each channel. Close a channel only when receivers need a completion signal, such as the end of a `range` loop.
- Close a channel once, after all sends finish. With several senders, one coordinator can wait for them and close the channel. Sending on or closing a closed channel panics.
- Use `<-chan T` and `chan<- T` in APIs when the caller needs only one direction. For a pointer, define whether the send transfers ownership. Synchronize access if it stays shared. Sending a slice or map does not copy the data it refers to.
- Choose buffer capacity for the intended handoff, work rate, and pressure on senders. A buffer does not replace cancellation. A sender can still block when the buffer is full.

## Cancellation and select

Let blocking sends and receives handle cancellation when the caller can stop waiting. A `select` gives cancellation no priority when several cases are ready. It cannot guarantee an immediate stop or that no other ready case runs.

```go
func forward(ctx context.Context, in <-chan Item, out chan<- Item) {
	for {
		var item Item
		select {
		case <-ctx.Done():
			return
		case value, ok := <-in:
			if !ok {
				return
			}
			item = value
		}

		select {
		case <-ctx.Done():
			return
		case out <- item:
		}
	}
}
```

The owner of `out` closes it after all senders finish. `forward` does not close it. Pass cancellation to other blocking operations, such as I/O, where supported. A bounded operation with a guaranteed completion path can end normally. It does not always need a context case in its `select`.

## Pipelines and workers

- If a later stage can stop early, let earlier senders stop too. Pass errors and cancellation to the right owner. Wait for started workers to exit.
- Limit concurrency when input size or the next stage's capacity requires it. Choose a fixed worker pool, semaphore, or existing group limit based on the work.
- Repeated timer creation in a busy loop may add allocations. Consider timer reuse if profiling shows a problem. Follow timer behavior for the project's Go version.
