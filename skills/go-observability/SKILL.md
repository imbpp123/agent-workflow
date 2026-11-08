---
name: go-observability
description: Use when implementing, changing, reviewing, or debugging Go services, jobs, handlers, or integrations, including their logs, metrics, and tracing.
---

# Go observability

Inspect the existing logging and telemetry conventions before changing code. Make the changed operational path observable using the project's stack. Do not assume an existing logger records the events the change needs.

## Logging

- For handlers, jobs, consumers, and external operations, consider what an operator needs to identify the operation and understand its outcome. Add structured logs for actionable failures, retries, degraded behavior, and meaningful lifecycle or business events where they are not already recorded. Avoid logging every call or expected outcome by default.
- Record an error at the boundary that handles it, with the operation and safe diagnostic context. Lower layers should normally return wrapped errors; avoid logging the same failure at every layer. An error that is handled, retried, or discarded still needs an appropriate signal when its outcome matters.
- Use stable, descriptive field names and suitable levels: debug for diagnostic detail, info for significant normal events, warn for degradation or recoverable problems, and error for failures needing attention. Follow project conventions and avoid noisy per-request success logs when existing middleware covers them.
- Never log credentials, tokens, raw request bodies, or sensitive personal data. Limit or redact other user-controlled values. Treat error messages and identifiers as potentially sensitive too.
- Pass the request context to logging and downstream operations when supported. Include request or trace identifiers when the existing integration provides them; context-aware logging alone does not guarantee trace fields appear in output.

## Other signals

- Use existing metrics for operation counts, failures, latency, or saturation when they help detect or diagnose the changed behavior. Choose bounded labels such as route templates and status classes; never use user IDs, raw URLs, or other unbounded values as metric labels. Prefer aggregatable histograms for latency when supported by the existing metrics stack.
- Preserve context propagation across HTTP, database, and messaging boundaries. Where tracing is already available, add spans at meaningful boundaries not already instrumented; end spans and record failures according to the tracing library. Avoid redundant spans and sensitive attributes.
- Use profiling, dashboards, and alerts when the task and operational needs justify them. Protect profiling endpoints and avoid exposing them publicly by default. Do not add an observability backend, dependency, dashboard, or product analytics just to satisfy a checklist.
- For new Go services without an established logger, consider standard-library `log/slog` if the supported Go version permits it. Do not migrate a working logger or telemetry stack unless requested.

## Verify

Test observable behavior at the relevant boundary, including failure and retry paths where applicable. Check useful fields and levels without coupling tests to incidental formatting; ensure sensitive values are not emitted. For metrics and traces, test the changed recording and propagation behavior when applicable. Verify integration through the real entry point or exporter when available; distinguish unit tests from proof of live delivery. If required instrumentation cannot be verified or is outside the task, report the gap.
