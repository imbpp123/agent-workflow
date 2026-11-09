# SQL formatting

Follow the project's SQL style. If there is no style, use uppercase keywords and put each major clause on a separate line. Indent fields, values, and conditions that span lines. Keep related expressions together; do not split every keyword.

For tables, put the opening parenthesis after the name. Put each column or table constraint on an indented line. Put the closing parenthesis on its own line:

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

Use this layout in SQL files and Go raw strings. Split query clauses, selected columns, and conditions across lines:

```sql
SELECT
    id,
    email
FROM users
WHERE active = $1
    AND created_at >= $2
ORDER BY id;
```

For inserts and updates, separate the operation, values or assignments, filters, and `RETURNING` clauses. Bind values as parameters. Formatting alone does not make SQL safe.
