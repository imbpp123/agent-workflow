# Queries and scanning

Use the caller's context and parameterized SQL with the project's database library. The snippets show native pgx v5 and assume `pool` is a `*pgxpool.Pool`; imports, types, and function signatures are omitted. For other libraries, use their equivalent APIs without migrating the existing layer.

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

`QueryRow` reports errors on `Scan` and discards rows after the first. Call `Scan` to return the connection to the pool. Ensure the query result is unique when required; if duplicates must be detected, use `Query` and check the count, or `pgx.CollectExactlyOneRow` where supported by the project's pgx version.

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

A query can return rows before reporting an error. Check `rows.Err()` before treating the whole result as successful; streaming with external side effects requires explicit handling of partial progress. For large results, use bounded pagination with a stable order or streaming instead of collecting an unbounded slice.

## Rules

- Map database outcomes according to the application contract; see [Database errors](errors.md).
- List selected columns explicitly and match `Scan` destinations to their order and types. For a nullable field `Name *string`, pass `&user.Name`; alternatively use a suitable `pgtype` nullable type. Preserve the distinction between NULL and a zero value.
- `pgx.CollectRows` and `pgx.RowToStructByName` are alternatives to manual scanning. Check their errors and field mapping, and confirm support in the project's pgx version. `CollectRows` closes rows but collects them in memory.
- Preallocate slice capacity when a reasonable result size is already known or bounded and the allocation is justified. Preserve the contract for nil versus empty results.
- Bind values with PostgreSQL placeholders; never concatenate user input into SQL. Placeholders do not represent identifiers or sort direction: map those inputs to fixed allowlists.
- For a list, use a compatible slice with `WHERE id = ANY($1)`. Define and test empty and nil input behavior: SQL distinguishes an empty array from a NULL array, including in logical expressions.
- Test missing and multiple rows where relevant, NULL and non-NULL values, scan and iteration errors, cancellation, and parameter binding. Use PostgreSQL integration tests for actual SQL and types; see [Testing database code](testing.md).
