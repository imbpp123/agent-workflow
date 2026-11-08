# Pool and performance

## Pool lifecycle

- Create a shared `pgxpool.Pool` at application startup, reuse it, and close it at shutdown. Do not create a pool per request or share one `*pgx.Conn` concurrently.
- Check errors from `ParseConfig` and `NewWithConfig`. Configure `MaxConns`, `MinConns`, `MaxConnLifetime`, and `MaxConnIdleTime` as needed. Budget connections across all application instances and other clients; never log credentials.
- Creating a pool does not prove the database is reachable. If startup requires connectivity, call `Ping` with a bounded context; close the pool if the check fails. A successful ping does not verify the schema or future queries.
- Pass a suitable context with a deadline to operations and connection acquisition, so a request cannot wait indefinitely for the pool.
- If the project uses PgBouncer, check pgx prepared-statement and query-mode compatibility with the PgBouncer version and pooling configuration; see the [pgx documentation](https://pkg.go.dev/github.com/jackc/pgx/v5#hdr-PgBouncer).
- Wire shutdown into the application's lifecycle: stop accepting requests and jobs, drain or cancel active work and wait for it to release acquired resources, then close the pool. Do not replace requested startup and shutdown wiring with a comment that a caller should drain work. If another component owns shutdown, integrate with it and verify the ordering. `Pool.Close()` waits for checked-out connections and has no context parameter.

## Returning connections

- `Pool.Query` holds a connection until `Rows` is closed; check `Rows.Err()`. `Pool.QueryRow` releases it when `Scan` is called. See [Queries and scanning](scanning.md).
- Release connections obtained with `Acquire`; close `BatchResults` from `SendBatch` and handle its error. Commit or roll back transactions. See [Transactions](transactions.md).
- For dedicated sessions such as long-running `LISTEN`, manage the connection lifetime explicitly. Clean up session state before returning a connection to the pool.

## Observability

- Export `pool.Stat()` through the project's existing metrics system, if configured. Record acquired, idle, and maximum connections as gauges; track acquisition counts, wait duration, and cancellations as cumulative counters or correct deltas, accounting for pool or process resets. Check metric availability for the project's pgx version.
- PostgreSQL server metrics are separate from pool metrics. If server monitoring is needed, reuse the existing infrastructure or managed-service collector: track connections, active queries waiting for locks, transaction rollbacks, and deadlocks over time. Use `pg_stat_activity` and `pg_stat_database` where available, with suitable read permissions; account for cumulative counter resets. Use `pg_stat_statements` for query statistics only when already available and appropriate.
- Send server metrics to the existing metrics backend if it supports them, including Sentry when configured for that signal. Avoid duplicate collection across application instances; do not add a collector, permissions, or PostgreSQL extensions without a task-specific need.
- Follow the project's existing logging and tracing conventions for database errors and query latency; avoid duplicate instrumentation. Do not include credentials, query parameters, or sensitive data in telemetry. Use Sentry only if the project already uses it and its configured SDK or integration supports the required signal; do not assume it collects pool metrics automatically.

## Testing and performance

- Test with PostgreSQL: startup failure, exhausted pool and canceled acquisition, resource release, and shutdown. For lifecycle wiring, test that new work stops and active work releases its resources before the pool closes. See [Testing database code](testing.md).
- Measure the existing representative workload before selecting an optimization. For a performance review with a disposable database and a representative workload, run a baseline measurement; create a benchmark if the project has none. Report unavailable measurements rather than assuming a speedup. Consider `SendBatch` or `CopyFrom` where appropriate, check operation and batch close errors, and commit or roll back any enclosing transaction. Use `EXPLAIN` safely on representative queries and choose indexes based on actual workload.
