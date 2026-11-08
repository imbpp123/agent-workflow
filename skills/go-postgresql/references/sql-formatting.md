# SQL formatting

Follow the project's existing SQL formatting conventions. Otherwise, use uppercase SQL keywords and put each major clause on a separate line. Indent fields, values, and conditions when splitting them across lines. Keep related expressions readable rather than splitting every keyword.

For table definitions, put the opening parenthesis after the table name, each column or table constraint on its own indented line, and the closing parenthesis on a separate line:

```sql
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY,
    email TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT users_email_unique UNIQUE (email)
);

COMMENT ON TABLE users IS 'Accounts that can access the application';
COMMENT ON COLUMN users.id IS 'Application-generated account identifier';
COMMENT ON COLUMN users.email IS 'Email address used to contact the account owner';
COMMENT ON COLUMN users.created_at IS 'Time when the account was created';
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
