---
name: go-postgresql
description: Use when writing, reviewing, or debugging Go code that accesses PostgreSQL, including queries, transactions, connection pools, and database tests.
---

# Go and PostgreSQL

## Library choice

Inspect the existing repository and follow its database conventions. For a new project without an established database library, use the native `pgx/v5` API and `pgxpool` for shared database access. A single `*pgx.Conn` is not safe for concurrent use. Native pgx gives direct access to PostgreSQL features such as `COPY`, `LISTEN/NOTIFY`, and PostgreSQL-specific types.

Do not migrate an existing database layer unless requested. Do not introduce an ORM or sqlx or `database/sql` without a clear need.

## Database operations

Keep SQL explicit and parameterized. Pass `context.Context` to all database calls. With native pgx, use `QueryRow(...).Scan(...)` for one row, `Query` for multiple rows, and `Exec` for statements without returned rows. Check `pgx.ErrNoRows` with `errors.Is`; translate it according to the domain. With another library, use its equivalent API and error types. Close rows and check iteration errors. Handle nullable values explicitly.

Use a transaction when operations must succeed or fail together. Choose locking and isolation based on the actual invariant; do not assume every update needs `FOR UPDATE`. Configure and monitor the pool based on the application's connection budget. Test business logic and failure paths; use PostgreSQL integration tests for actual SQL and transaction behavior.

For schema changes and migrations, follow the project's existing process, consider production data and locking, and require appropriate review. Do not change schema unless the task calls for it.

## References

- [Queries and scanning](references/scanning.md): parameters, missing rows, iteration, nullable values and dynamic sorting.
- [Database errors](references/errors.md): domain outcomes, PostgreSQL error codes and diagnostic boundaries.
- [Transactions](references/transactions.md): atomic operations, rollback, isolation and retries.
- [Pool and performance](references/performance.md): pool configuration, batch operations and query analysis.
- [Testing](references/testing.md): unit and PostgreSQL integration test boundaries.

Read the relevant references before implementing or reviewing the corresponding operations, including pool startup and shutdown, transactions, errors, and database tests. Apply their PostgreSQL guidance to the existing database library; pgx-specific APIs and examples apply only when native pgx is used. For pgx, check the project's version and the [official pgx documentation](https://pkg.go.dev/github.com/jackc/pgx/v5) for API details.
