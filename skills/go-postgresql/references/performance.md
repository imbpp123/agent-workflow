# Pool and performance

## Pool lifecycle

- Create a shared `pgxpool.Pool` at startup. Reuse it and close it at shutdown. Do not create a pool per request or use one `*pgx.Conn` concurrently.
- Check errors from `ParseConfig` and `NewWithConfig`. Set `MaxConns`, `MinConns`, `MaxConnLifetime`, and `MaxConnIdleTime` as needed. Count connections across all application instances and other clients. Never log credentials.
- Creating a pool does not prove PostgreSQL is reachable. If startup requires a connection, call `Ping` with a bounded context. Close the pool if it fails. A successful ping does not check the schema or future queries.
- Use contexts with suitable deadlines for operations and connection acquisition. A request must not wait forever for the pool.
- For PgBouncer, check prepared-statement and query-mode support for the actual pgx version, PgBouncer version, and pooling settings. See the [pgx documentation](https://pkg.go.dev/github.com/jackc/pgx/v5#hdr-PgBouncer).
- Connect shutdown to the application lifecycle. Stop new requests and jobs. Drain or cancel active work, then wait for it to release resources. Close the pool last. Implement requested startup and shutdown wiring; a comment telling the caller to drain work is not enough. If another component owns shutdown, use it and verify the order. `Pool.Close()` waits for acquired connections and has no context parameter.

## Returning connections

- `Pool.Query` holds a connection until `Rows` is closed. Check `Rows.Err()`. `Pool.QueryRow` releases its connection when `Scan` is called. See [Queries and scanning](scanning.md).
- Release connections from `Acquire`. Close `BatchResults` from `SendBatch` and check the close error. Commit or roll back transactions. See [Transactions](transactions.md).
- For a dedicated session, such as a long-running `LISTEN`, manage its connection lifetime. Clear session state before returning the connection to the pool.

## Observability

- Export `pool.Stat()` through the existing metrics system, if configured. Record acquired, idle, and maximum connections as gauges. Record acquisition counts, wait duration, and cancellations as cumulative counters or correct deltas. Handle pool and process resets. Check which metrics the project's pgx version supports.
- Server metrics are separate from pool metrics. If server monitoring is needed, reuse the existing collector or managed service. Track connections, active queries waiting for locks, transaction rollbacks, and deadlocks over time. Use `pg_stat_activity` and `pg_stat_database` when available with the required read access. Account for cumulative counter resets. Use `pg_stat_statements` only if it is already available and fits the task.
- Send server metrics to the existing backend if it supports them. This includes Sentry when configured for that signal. Avoid duplicate collection across application instances. Add collectors, permissions, or PostgreSQL extensions only for a current task need.
- Follow existing logging and tracing rules for database errors and query time. Use [go-observability](../../go-observability/SKILL.md) for general policy when available. Avoid duplicate instrumentation and sensitive telemetry, including credentials and query parameters. Use Sentry only if the project already uses it and its SDK or integration supports the signal. Do not assume it collects pool metrics automatically.

## Testing and performance

- Test startup failure, canceled acquisition from an exhausted pool, resource release, and shutdown on PostgreSQL. Check that new work stops and active work releases resources before pool close. See [Testing database code](testing.md).
- Measure a representative workload before choosing an optimization. For a performance review, run a baseline on a disposable database. Add a benchmark if none exists. Report missing measurements; do not assume a speedup. Consider `SendBatch` or `CopyFrom` when useful. Check operation and batch close errors. Finish any enclosing transaction. Use `EXPLAIN` safely on representative queries and choose indexes for the actual workload.
