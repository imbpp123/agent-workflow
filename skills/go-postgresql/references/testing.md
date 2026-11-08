# Testing PostgreSQL code

## Unit tests

- Test repository and application behavior with existing fakes or small interfaces where useful: expected results, not-found contracts, error mapping, cancellation, and failure paths. Keep tests deterministic; avoid coupling to exact SQL or call order unless required by the contract.
- Fakes do not validate SQL, PostgreSQL types, constraints, transaction isolation, or pgx behavior. Use integration tests for those.

## Integration tests

- Exercise the real repository entry point with the project's database library and a disposable PostgreSQL instance using the project's supported versions and migrations. Follow existing setup; do not add test dependencies without a reason or use production credentials.
- Isolate test data and clean up resources even on failure. Use separate databases or schemas when needed. A test transaction only isolates operations that actually use that transaction; it cannot roll back commits on other connections.
- Cover applicable paths: parameter binding, zero/one/multiple rows, `NULL` and non-`NULL` values, empty inputs, type mapping, constraints, domain error mapping, and query cancellation.
- Compare timestamp instants with `time.Time.Equal`, rather than comparing `time.Time` structs, and account for PostgreSQL timestamp precision. Exercise timezone-sensitive tests outside UTC as well.
- For transactions, verify successful commits and that a later failure rolls back earlier writes. Test relevant concurrent invariants and retry behavior with separate connections and explicit synchronization; avoid sleeps. Use bounded contexts and ensure goroutines and database resources are cleaned up.
- For pool lifecycle, cover startup failure, canceled acquisition when the pool is exhausted, resource release, and shutdown where applicable. Use controlled deadlines and synchronization rather than relying on timing alone.
- Run the project's documented checks. If PostgreSQL or its runtime is unavailable, report integration tests as not run; do not present mocks or skipped tests as integration coverage. When CI configuration is in scope, make required integration tests fail clearly if the database is missing.
