# Transactions

Use one transaction for operations that must succeed or fail together. This example creates an order and its audit record with pgx v5 and Go 1.21 or later; imports and schema are omitted.

```go
func createOrder(ctx context.Context, pool *pgxpool.Pool, customerID int64) (int64, error) {
    tx, err := pool.Begin(ctx)
    if err != nil {
        return 0, fmt.Errorf("begin transaction: %w", err)
    }
    defer func() {
        rollbackCtx, cancel := context.WithTimeout(context.WithoutCancel(ctx), 2*time.Second)
        defer cancel()

        if err := tx.Rollback(rollbackCtx); err != nil && !errors.Is(err, pgx.ErrTxClosed) {
            slog.ErrorContext(rollbackCtx, "rollback failed")
        }
    }()

    var orderID int64
    err = tx.QueryRow(ctx,
        `INSERT INTO orders (customer_id)
        VALUES ($1)
        RETURNING id`, customerID,
    ).Scan(&orderID)
    if err != nil {
        return 0, fmt.Errorf("create order: %w", err)
    }

    _, err = tx.Exec(ctx,
        `INSERT INTO order_events (order_id, event)
        VALUES ($1, $2)`, orderID, "created",
    )
    if err != nil {
        return 0, fmt.Errorf("create order event: %w", err)
    }
    if err := tx.Commit(ctx); err != nil {
        return 0, fmt.Errorf("commit transaction: %w", err)
    }
    return orderID, nil
}
```

The caller's context controls begin, queries, and commit. Canceling it does not automatically roll back a native pgx transaction, and a rollback using the canceled context may fail immediately. Here, `context.WithoutCancel(ctx)` preserves values but removes cancellation and the deadline; `context.WithTimeout` sets a new deadline. Two seconds is an example, not a default. Cleanup can delay return after cancellation. For Go versions before 1.21, use an appropriate separate bounded cleanup context.

A deferred rollback after a successful commit returns `pgx.ErrTxClosed`, which is expected. Handle other errors according to the application. The example logs the failure without the raw error; add only approved safe diagnostic fields, as described in [Database errors](errors.md). A separate context cannot guarantee success: the connection may already be closed. If rollback of a real transaction fails, pgx closes the connection. Do not use an unbounded cleanup context.

Describe commit outcomes accurately in code and reports: `pgx.ErrTxCommitRollback` confirms rollback, but a network error during commit can leave the outcome unknown. Do not say that every failure rolled back; a later cleanup attempt or `pgx.ErrTxClosed` does not prove the outcome of an uncertain commit.

## Rules

- Execute all related queries through the same `tx`, including queries in repository methods. A query through `pool` is outside that transaction.
- Check `RowsAffected()` for `UPDATE` or `DELETE` when the number of changed rows affects the invariant.
- Use `BeginTx` with `pgx.TxOptions` when a non-default isolation level is required. Use `SELECT ... FOR UPDATE` when the invariant needs row locks and acquire locks in a consistent order. Row locks do not protect absent rows or every invariant; consider constraints, other synchronization, or serializable isolation as appropriate.
- On a retryable serialization failure (`40001`) or deadlock (`40P01`), retry the entire operation in a new transaction. Bound attempts, use backoff, respect context cancellation, and avoid repeating external side effects. A commit error can leave the outcome uncertain; do not blindly retry non-idempotent work. See [Database errors](errors.md) for error classification.
- After a SQL error, PostgreSQL normally marks the transaction as failed. Roll it back; use a savepoint when partial recovery is required.
- Test success, rollback after a later operation fails, cancellation, and relevant concurrent behavior against PostgreSQL. See [Testing database code](testing.md).
