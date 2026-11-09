---
name: go-observability
description: Use when changing or checking how Go services, jobs, handlers, or integrations run, fail, retry, or stop, and when working on logs, metrics, or traces.
---

# Go observability

When behavior changes, check which events and failures need an operational signal. Reuse existing logs, metrics, and traces. Add a signal when the changed behavior needs one and existing instrumentation does not provide it. The presence of a logger alone does not prove that these events are recorded.

Changes to names or formatting alone do not require new telemetry. Follow the project's logging and telemetry conventions.

## Logging

- For handlers, jobs, consumers, and external calls, identify what an operator needs to know about the outcome. Use structured logs for failures that need attention, retries, degraded behavior, and meaningful lifecycle or business events. Check whether these events are already recorded. Avoid logging every call or expected result by default.
- Record an error at the boundary that handles it. Include the operation and safe diagnostic context. Lower layers normally return errors with useful context. A handled, retried, or discarded error still needs a signal when its outcome matters. Avoid logging the same failure at every layer.
- Use stable, clear field names. Use debug for diagnostic detail, info for significant normal events, warn for degraded behavior or recoverable problems, and error for failures that need attention. Follow project levels. Reuse request success logs already supplied by middleware.
- Never log credentials, tokens, raw request bodies, or sensitive personal data. Limit or redact other user-controlled values. Treat error messages and identifiers as potentially sensitive too.
- Pass the request context to logging and downstream calls when supported. Include request or trace identifiers when the existing integration provides them. Check the actual output for these fields. Passing context to a logger alone does not guarantee trace fields.

For error wrapping, read [Go code style](../go-code-style/SKILL.md). For driver error classification and safe database diagnostics, read [Go PostgreSQL errors](../go-postgresql/references/errors.md).

## Other signals

- Use existing metrics for operation counts, failures, latency, or saturation when they help diagnose the changed behavior. Use bounded labels such as route templates and status classes. Never use user IDs, raw URLs, or other unbounded values as labels. Prefer latency histograms that can be combined across instances when the metrics stack supports them.
- Preserve context across HTTP, database, and messaging boundaries. When tracing is available, add spans at meaningful boundaries that lack them. End spans and record failures as required by the tracing library. Avoid duplicate spans and sensitive attributes.
- Use profiling, dashboards, and alerts when the task and operational needs justify them. Protect profiling endpoints. Public access needs a clear reason and suitable access controls. Add a backend, dependency, dashboard, or product analytics only when the task needs it.
- For new Go services without an established logger, consider standard-library `log/slog` if the supported Go version permits it. Do not migrate a working logger or telemetry stack unless requested.

## Verify

Test the signals at the relevant boundary, including failures and retries where needed. Check fields and levels without relying on incidental formatting. Check that sensitive values are absent from output. For metrics and traces, test the changed recording and context propagation.

Verify integration through the real entry point or exporter when available. Unit tests do not prove live delivery. Report required signals that are outside the task or cannot be verified. For general test tools and commands, read [Go testing](../go-testing/SKILL.md).
