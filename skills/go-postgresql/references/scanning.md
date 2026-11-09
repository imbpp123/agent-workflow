# Queries and scanning

Use the caller's context and bind SQL values with the project's database library. These snippets use native pgx v5 and a `*pgxpool.Pool` named `pool`. Imports, types, and function signatures are omitted. For other libraries, use their APIs and keep the existing database layer.

## One row

```go
var user User
err := pool.QueryRow(ctx,
    `SELECT
        id,
        name
    FROM users
    WHERE id = $1`, id,
).Scan(&user.ID, &user.Name)
if errors.Is(err, pgx.ErrNoRows) {
    return nil, ErrUserNotFound
}
if err != nil {
    return nil, fmt.Errorf("query user: %w", err)
}
return &user, nil
```

`QueryRow` reports errors on `Scan`. It discards rows after the first. Call `Scan` to release the connection. Ensure results are unique when the contract requires it. To detect duplicates, use `Query` and check the count, or use `pgx.CollectExactlyOneRow` if the project's version supports it.

## Multiple rows

```go
rows, err := pool.Query(ctx, `SELECT
    id,
    name
FROM users
WHERE active = $1`, true)
if err != nil {
    return nil, fmt.Errorf("query users: %w", err)
}
defer rows.Close()

var users []User
for rows.Next() {
    var user User
    if err := rows.Scan(&user.ID, &user.Name); err != nil {
        return nil, fmt.Errorf("scan user: %w", err)
    }
    users = append(users, user)
}
if err := rows.Err(); err != nil {
    return nil, fmt.Errorf("read users: %w", err)
}
return users, nil
```

A query can return rows before an error. Check `rows.Err()` before treating the full result as successful. When streaming causes external side effects, handle partial progress explicitly. For large results, use bounded pages with stable ordering or stream rows. Do not collect an unbounded slice.

## Rules

- Map database results to the application contract. The snippets wrap errors for internal use; `%w` does not hide driver types or sensitive text. Translate or sanitize at the required boundary. See [Database errors](errors.md).
- List selected columns explicitly. Match `Scan` targets to their order and types. For a nullable `Name *string`, pass `&user.Name`, or use a suitable nullable `pgtype` type. Keep NULL distinct from a zero value. Keep driver-specific types inside the adapter.
- `pgx.CollectRows` and `pgx.RowToStructByName` can replace manual scanning. Check errors, field mapping, and support in the project's pgx version. `CollectRows` closes rows but stores the results in memory.
- Set slice capacity in advance when the result size is known or bounded and it helps. Keep the contract for nil and empty results.
- Bind values with PostgreSQL placeholders. Never join user input into SQL. Placeholders cannot stand for identifiers or sort direction. Map those inputs to fixed allowed values.
- For a list, use a compatible slice with `WHERE id = ANY($1)`. Define and test empty and nil inputs. SQL treats an empty array and a NULL array differently, including in logical expressions.
- Test missing and multiple rows when relevant, NULL and non-NULL values, scan and iteration errors, cancellation, and parameter binding. Use PostgreSQL tests for actual SQL and types. See [Testing database code](testing.md).
