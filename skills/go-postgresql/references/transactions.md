# Transactions

Use one transaction for operations that must succeed or fail together. The application decides which writes form one operation. The database adapter runs them in one SQL transaction and keeps driver types private. Use [go-clean-architecture](../../go-clean-architecture/SKILL.md) for these application boundaries when available.

This private adapter helper creates an order and its audit event. It uses native pgx v5. Its cleanup code needs Go 1.21 or later; check the chosen pgx release's Go requirement too. Imports and schema are omitted. Both IDs come from the application. Here, `uuid.UUID` is the UUID type already used by the project. Use the project's representation and generator; do not add a UUID library just to copy this example. The `orders.id` column is UUID with no database default.

```go
func createOrder(ctx context.Context, pool *pgxpool.Pool, orderID, customerID uuid.UUID) error {
    tx, err := pool.Begin(ctx)
    if err != nil {
        return fmt.Errorf("begin transaction: %w", err)
    }
    defer func() {
        rollbackCtx, cancel := context.WithTimeout(context.WithoutCancel(ctx), 2*time.Second)
        defer cancel()

        if err := tx.Rollback(rollbackCtx); err != nil && !errors.Is(err, pgx.ErrTxClosed) {
            slog.ErrorContext(rollbackCtx, "rollback failed")
        }
    }()

    _, err = tx.Exec(ctx,
        `INSERT INTO orders (id, customer_id)
        VALUES ($1, $2)`, orderID, customerID,
    )
    if err != nil {
        return fmt.Errorf("create order: %w", err)
    }

    _, err = tx.Exec(ctx,
        `INSERT INTO order_events (order_id, event)
        VALUES ($1, $2)`, orderID, "created",
    )
    if err != nil {
        return fmt.Errorf("create order event: %w", err)
    }
    if err := tx.Commit(ctx); err != nil {
        return fmt.Errorf("commit transaction: %w", err)
    }
    return nil
}
```

The caller's context controls begin, queries, and commit. Canceling it does not roll back a native pgx transaction automatically. Rollback with the canceled context may fail at once. `context.WithoutCancel(ctx)` keeps context values but removes cancellation and the deadline. `context.WithTimeout` sets a new deadline. Two seconds is an example, not a default. Cleanup can delay the return after cancellation. Before Go 1.21, use another separate cleanup context with a timeout.

A deferred rollback after commit returns `pgx.ErrTxClosed`. This is expected. Handle other errors under the application's policy. This example logs only a safe message. Add only approved safe fields; see [Database errors](errors.md). A separate context does not guarantee cleanup: the connection may already be closed. If rollback of a real transaction fails, pgx closes the connection. Always bound cleanup time.

The helper wraps errors with `%w` for internal handling. These errors still expose driver types and may contain sensitive text. Translate them before crossing a repository boundary that must hide driver types. Apply the project's safe output policy before logging or returning them to a client. Use the project's logger in real code.

Report commit results accurately. `pgx.ErrTxCommitRollback` confirms rollback. A network error during commit can leave the result unknown. Do not say every failure rolled back. A later cleanup attempt or `pgx.ErrTxClosed` does not prove whether an uncertain commit succeeded.

## Rules

- Run all related queries through the same `tx`, including repository calls. A query through `pool` runs outside that transaction.
- Check `RowsAffected()` for `UPDATE` or `DELETE` when the row count affects the data rule.
- Use `BeginTx` and `pgx.TxOptions` when the default isolation level is not enough. Use `SELECT ... FOR UPDATE` when the rule needs row locks. Take locks in a fixed order. Row locks do not protect missing rows or every rule. Consider constraints, other synchronization, or serializable isolation as needed.
- For retryable serialization failures (`40001`) or deadlocks (`40P01`), retry the whole operation in a new transaction. Limit attempts, use backoff, and respect cancellation. Do not repeat external side effects. An uncertain commit needs a safe recovery policy; do not blindly retry work that may run twice. See [Database errors](errors.md) for classification.
- After a SQL error, PostgreSQL usually marks the transaction as failed. Roll it back. Use a savepoint only when partial recovery is needed, and check savepoint and rollback errors.
- Test success, rollback after a later write fails, cancellation, and relevant concurrent work on PostgreSQL. See [Testing database code](testing.md).
