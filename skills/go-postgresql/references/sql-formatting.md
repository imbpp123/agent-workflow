# SQL formatting

Follow the project's existing SQL formatting conventions. Otherwise, use uppercase SQL keywords and put each major clause on a separate line. Indent fields, values, and conditions when splitting them across lines. Keep related expressions readable rather than splitting every keyword.

For table definitions, put the opening parenthesis after the table name, each column or table constraint on its own indented line, and the closing parenthesis on a separate line:

```sql
CREATE TABLE IF NOT EXISTS users (
    id BIGINT PRIMARY KEY,
    email TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT users_email_unique UNIQUE (email)
);
```

Apply the same layout in SQL files and Go raw strings. For queries, separate clauses and put multiple selected columns or conditions on their own lines:

```sql
SELECT
    id,
    email
FROM users
WHERE active = $1
    AND created_at >= $2
ORDER BY id;
```

For inserts and updates, separate the operation, values or assignments, filters, and `RETURNING` clauses. Use parameters for values; formatting does not replace parameterization.
