---
name: go-clean-architecture
description: Use when designing, implementing, or reviewing a Go application that uses Clean Architecture.
---

# Clean Architecture in Go

Use these rules when the project uses Clean Architecture or the user asks for it. Otherwise, follow the project's current architecture.

- Follow the project's Go version and package layout.
- Group packages by responsibility. Add a layer only when it has a clear purpose.
- Keep existing boundaries during focused changes. Do not force a fixed folder structure.

## Boundaries

- Keep imports pointing inward. Infrastructure and delivery can import application and domain. Application can import domain. Domain must not import application. Neither application nor domain may import infrastructure or delivery.
- When one module calls another module's service, use an interface defined by the caller. Include only the methods the caller needs.
- Use data types and pure functions directly when the import direction is allowed.
- Define ports in the inner layer that uses them. A port is an interface for an external capability. Implement it in an outer adapter.
- Create and connect dependencies with constructors or factory functions at the application entry point. Do not use a DI framework.

## Domain

- Put business rules in entities and value objects. Change state through domain behavior. Reject changes that break business rules.
- Use a domain service only when a business rule or calculation does not belong to one entity or value object.
- Use domain types in domain services. Keep persistence, transport, and use case steps out of them.
- Keep SQL, HTTP, frameworks, and infrastructure models out of the domain.

## Application services

- Use an application service to run one use case. Load data and save results through ports when needed. Call domain behavior to apply business rules.
- Coordinate transactions and external calls here when the use case needs them.
- When a business rule needs external data, load it through a port. Pass the data to the domain to apply the rule.

## Repositories and adapters

- Use repositories for SQL, data mapping, and storage error translation. Their writes must join the use case's transaction when they must commit together.
- Use handlers to read requests and build responses. Map errors to the response contract.
- Use external clients to map requests and responses for external APIs.
- Keep business decisions and use case steps out of repositories and adapters. Delegate them to application or domain code.
- Check request format in delivery adapters. Check business rules in the domain so all entry points use the same rules.

## Data and errors

- Keep transport, database, and driver types out of domain and application contracts.
- Add data types for a boundary when needed. Create a separate DTO only when that boundary needs it.
- Translate expected errors at module boundaries. Keep unexpected infrastructure failures distinct from business results.
- Keep internal error details out of public responses.

For Go names and error wrapping, read [Go code style](../go-code-style/SKILL.md). Use the boundary's contract to decide which error types callers may inspect.

## Transactions and external calls

- The use case defines which writes must succeed or fail together.
- Infrastructure opens, commits, and rolls back the database transaction through an application port. All participating repository writes use that transaction. Keep driver transaction types out of the application contract.
- Use atomic storage constraints or concurrency control when needed to protect business rules during concurrent requests.
- A database transaction cannot make an external API call part of the same atomic operation. Handle retries and partial failures. Use idempotency to prevent duplicate effects when a request is repeated.

For PostgreSQL transaction APIs, isolation, and retries, read [Go PostgreSQL](../go-postgresql/SKILL.md).

## Tests

- Test domain rules and invalid states without infrastructure.
- Test use cases with test implementations of their ports. Cover dependency failures.
- Use integration tests for real adapters, SQL, and transaction boundaries.

For test tools and verification commands, read [Go testing](../go-testing/SKILL.md).
