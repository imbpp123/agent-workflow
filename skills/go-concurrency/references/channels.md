# Channels and pipelines

## Channel ownership

- Use channels to communicate or coordinate when they make ownership and flow clear. Choose a mutex for shared state when it is simpler.
- Define who sends, receives, and, if needed, closes each channel. A channel needs closing only when receivers need a completion signal, such as ending a `range` loop.
- Close a channel once, after all sends are finished. With multiple senders, a coordinator can wait for them and close the channel. Sending on or closing an already closed channel panics.
- Use `<-chan T` and `chan<- T` in APIs when the caller needs only one direction. Sending a pointer is valid, but define whether ownership transfers or access remains synchronized. Sending a slice or map value does not copy its underlying data.
- Choose buffer capacity based on the intended handoff, throughput, and backpressure. A buffer does not replace cancellation or guarantee that a sender will not block.

## Cancellation and select

Make potentially blocking sends and receives cancellable when the caller can abandon the operation. A `select` does not prioritize cancellation if multiple cases are ready, so do not rely on it for an immediate or exclusive stop.

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

The owner of `out` closes it when all senders have finished; `forward` does not close it. Cancellation must also reach other blocking operations, such as I/O, where supported. Not every `select` needs a context case: a bounded operation with a guaranteed completion path can end normally.

## Pipelines and workers

- If a downstream stage can stop early, ensure upstream senders can also stop. Propagate errors and cancellation and wait for started workers to exit.
- Bound concurrency when input size or downstream capacity requires it. A fixed worker pool, semaphore, or existing group limit can provide the bound; select based on the workload.
- A timer created repeatedly in a hot loop may add allocations. If profiling shows a problem, consider reusing a timer; follow the timer semantics for the project's Go version.
