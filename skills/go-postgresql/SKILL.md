---
name: go-postgresql
description: Use when writing, reviewing, or debugging Go code that accesses PostgreSQL, including queries, transactions, connection pools, and database tests.
---

# Go and PostgreSQL

## Library choice

Read the repository and follow its database conventions. For a new project with no database library, use native `pgx/v5` and `pgxpool` for shared access. One `*pgx.Conn` is not safe for concurrent use. Native pgx supports PostgreSQL features such as `COPY`, `LISTEN/NOTIFY`, and database-specific types.

Keep an existing database layer unless the task asks to change it. Do not add an ORM, sqlx, or `database/sql` without a clear need.

## Database operations

Write explicit SQL and bind values as parameters. Pass `context.Context` to database calls. With native pgx, use `QueryRow(...).Scan(...)` for one row, `Query` for several rows, and `Exec` when no rows are returned. Check `pgx.ErrNoRows` with `errors.Is` and follow the application's not-found contract. For another library, use its APIs and error types. Close rows, check iteration errors, and handle NULL values.

Split SQL across lines. Follow the project's style or use [SQL formatting](references/sql-formatting.md).

Use one transaction for writes that must succeed or fail together. Honor repository contracts that hide driver types. Choose locks and isolation for the rule the data must meet; not every update needs `FOR UPDATE`. Size and monitor the pool within the application's connection budget. Use real PostgreSQL tests for SQL and transaction behavior.

This skill owns PostgreSQL queries, errors, transactions, pools, migrations, and database checks. Use [go-clean-architecture](../go-clean-architecture/SKILL.md) for application transaction boundaries, [go-testing](../go-testing/SKILL.md) for general test rules, and [go-observability](../go-observability/SKILL.md) for general logging policy when available. This skill keeps the database-specific rules below and in its references.

## Migrations

Follow the existing migration tool, layout, and process. For a new project with no migration process, use Goose as a library. Put the entry point in `cmd/migrate`, runner code in `internal/migration`, and SQL files in `internal/migration/sql`. Embed SQL files in the migration binary so it needs no runtime file paths. Use pgx's `database/sql` adapter for Goose. The application can still use native pgx and `pgxpool`. Run migrations in a separate deployment step, not at application startup.

Change schema only when the task needs it. Consider production data, locks, and the required review.

### Rules

- Follow the project's migration test boundary. Apply schema-only migrations with the real command on a disposable database. Do not add catalog tests for every table, column, or index unless required. Test runner logic separately. For data changes, check the result with representative existing data.
- Before adding a constraint that creates an index, name the data rule and required index. For a meaningful trade-off, explain its cost and the alternative. State which guarantee is lost without the constraint.
- Add a PostgreSQL comment for each new table to explain its purpose.
- Add a PostgreSQL comment for each new column to explain its meaning and use.
- Comment on each index you create explicitly. Name the query or constraint it supports. Review the comment when queries change. Indexes created by `PRIMARY KEY` and `UNIQUE` constraints need no separate comments.
- Use UUID for new entity IDs and references to those IDs. Generate IDs in the application and pass them in SQL. Do not add database ID defaults or generators.
- Use the project's UUID representation. Keep existing ID types and public contracts during focused changes. Moving existing identifiers to UUID is a separate migration task.

## References

- [SQL formatting](references/sql-formatting.md): layout for migrations and queries.
- [Queries and scanning](references/scanning.md): parameters, missing rows, iteration, nullable values and dynamic sorting.
- [Database errors](references/errors.md): domain outcomes, PostgreSQL error codes and diagnostic boundaries.
- [Transactions](references/transactions.md): atomic operations, rollback, isolation and retries.
- [Pool and performance](references/performance.md): pool configuration, batch operations and query analysis.
- [Testing](references/testing.md): unit and PostgreSQL integration test boundaries.

Read the relevant references before changing or reviewing these operations. This includes pool startup and shutdown, transactions, errors, and database tests. Apply PostgreSQL rules to the existing database library. Use pgx APIs and examples only for native pgx. Check the project's pgx version and the [official pgx documentation](https://pkg.go.dev/github.com/jackc/pgx/v5) for API support.
