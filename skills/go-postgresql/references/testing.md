# Testing PostgreSQL code

Use [go-testing](../../go-testing/SKILL.md) for general test design when available. This reference covers PostgreSQL behavior and the checks that fakes cannot replace.

## Unit tests

- Use existing fakes or small interfaces to check repository results, not-found contracts, error mapping, cancellation, and failure paths. Keep tests deterministic. Match exact SQL or call order only when the contract requires it.
- Fakes do not check SQL, PostgreSQL types, constraints, transaction isolation, or pgx behavior. Use integration tests for these.

## Integration tests

- Call the real repository entry point with the project's database library. Use a disposable PostgreSQL instance, supported versions, and project migrations. Follow the existing setup. Add test dependencies only with a reason. Do not use production credentials.
- Isolate data and clean up resources even after failures. Use separate databases or schemas when needed. A test transaction covers only calls that use it. It cannot undo commits on other connections.
- Cover relevant paths: bound parameters, zero/one/multiple rows, NULL and non-NULL values, empty inputs, type mapping, constraints, domain error mapping, and query cancellation.
- Compare timestamp instants with `time.Time.Equal`, not struct equality. Account for PostgreSQL timestamp precision. Run timezone-sensitive tests outside UTC too.
- Check successful commits and rollback of earlier writes after a later failure. Check relevant concurrent data rules and retries with separate connections and explicit synchronization. Do not use sleeps to guess the order. Bound contexts and clean up goroutines and database resources.
- For pools, check startup failure, canceled acquisition from an exhausted pool, resource release, and shutdown where relevant. Use controlled deadlines and synchronization, not timing alone.
- Run the project's documented checks. If PostgreSQL or its runtime is missing, report integration tests as not run. Mocks and skipped tests do not prove integration behavior. If CI changes are in scope, make required integration tests fail clearly when the database is missing.
