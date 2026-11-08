---
name: go-clean-architecture
description: Use when designing, implementing, or reviewing a Go application that uses Clean Architecture.
---

# Clean Architecture in Go

Apply these rules when Clean Architecture is requested or already used. Otherwise, follow the project's existing architecture. Go imports point inward: infrastructure and delivery depend on application and domain, never the reverse. An outer adapter implements a port defined by its inner consumer, so the use case can call external capabilities without importing their implementations.

## Boundaries

- **Domain:** entities and value objects own business rules and invariants. Enforce state changes through domain behavior. Keep SQL, HTTP, frameworks, and infrastructure models out of the domain.
- **Domain service:** holds a business rule or calculation that does not naturally belong to one entity or value object, such as a pricing rule involving several domain objects. Use domain types; keep persistence, transport, and use-case orchestration out. Do not create a service when an entity or value object owns the rule.
- **Application service / use case:** orchestrates one application operation: obtain data through ports, call domain behavior, persist results, and coordinate transactions or external effects as needed. It controls the workflow; domain invariants stay in the domain. Define small interfaces at the consumer boundary when needed; do not create an interface for every type.
- **Repositories:** implement persistence with SQL, data mapping, transactions, and persistence error translation. Do not make business decisions or orchestrate use cases here.
- **Delivery and external adapters:** handlers translate requests, responses, and errors; clients translate external APIs. Delegate business decisions to the application or domain.
- **Composition root:** construct and connect concrete dependencies at the application entry point. Do not require a DI framework.

Validate request shape in delivery adapters and business invariants in the domain, so all entry points enforce the same rules. When a rule needs external data, the use case obtains it through a port and passes it to domain behavior. Use atomic storage constraints or concurrency control when needed to protect invariants across concurrent requests.

Keep transport, database, and driver types out of domain and application contracts; use boundary data types when needed, not a separate DTO for every entity. Translate expected errors at boundaries without turning unexpected infrastructure failures into business outcomes or exposing internal details. Let the use case define the atomic operation and infrastructure manage its transaction, including across repositories, through an application port rather than a driver transaction type. A database transaction cannot make an external API call atomic; account for retries, idempotency, and partial failures.

Follow the project's Go version and package layout. Organize packages around responsibilities; do not impose a fixed directory tree or add layers for their own sake. Preserve existing boundaries during focused changes. Test domain rules and invalid states without infrastructure; test use cases with substitute ports, including dependency failures. Use integration tests for actual adapters, SQL, and transaction boundaries.

