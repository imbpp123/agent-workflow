# Go style reference

## Naming and APIs

- Use short, clear Go names and standard acronyms such as `HTTPServer`, `userID`, and `URL`. Keep package names short and lowercase; avoid repeating the package name in exported identifiers.
- Keep interfaces small and near their consumers when useful. Preserve public APIs unless a change is required.
- Handle errors explicitly and add operation context. Wrap with `%w` when callers need `errors.Is` or `errors.As`; avoid logging and returning the same error at every layer. Reserve `panic` for unrecoverable programming errors.
- Propagate the caller's context when cancellation or deadlines are needed. Avoid storing it in structs unless an established API requires it. Release resources on every path; use `defer` where it makes ownership clear.

## Declarations and values

- Use `:=` for local values when it improves clarity; use `var` when the zero value is useful or the type should be explicit.
- A nil slice is valid. Choose nil or empty slices according to the API contract, especially for JSON. Initialize a map before writing to it.
- Use named fields in struct literals when they make the code clear or protect against field changes. Follow the type's established usage.
- Pass simple values such as `string`, `int`, `bool`, and `time.Time` by value unless a pointer has a clear purpose. Copying a value does not necessarily copy data it refers to.
- Use pointer parameters when the function must change the original value, share its identity, avoid copying a non-copyable value, or represent an optional value with `nil`. A pointer is not a default performance optimization; benchmark when copying cost matters.
- Maps and slices can refer to shared data even when passed by value. Do not copy a struct containing a `sync.Mutex` after the mutex has been used.

```go
func FormatUser(name string, createdAt time.Time) string
func SetDefaults(cfg *Config) // changes cfg
func UpdateName(ctx context.Context, name *string) error // nil means unchanged
```

These rules apply to function parameters. Choose method receivers based on the type and its methods; keep receiver choices consistent where practical.

## Control flow and functions

- Handle errors and exceptional cases early when this reduces nesting. Omit `else` after a branch that exits.
- Use `switch` for clear alternatives. Extract complex conditions only when the names explain intent; preserve short-circuit evaluation and side effects.
- Keep functions focused. Prefer a small number of parameters, but introduce a struct only when the values belong together or it improves the API.
- Put `context.Context` first when a function needs it. Avoid naked returns when the returned values are not immediately clear.
- Prefer `range` when it makes iteration clearer. Use language features supported by the project's Go version.

For example, name the cheap checks and leave a later check in the condition so it runs only when needed:

```go
isAdmin := user.Role == RoleAdmin
isOwner := resource.OwnerID == user.ID
if isAdmin || isOwner || hasPermission(user, resource) {
	allow()
}
```

Do not move `hasPermission` into a variable before the condition: that would call it even when an earlier check succeeds. The same applies to checks that rely on earlier guards, such as a nil check.

## Layout and organization

- Break long lines at meaningful boundaries when it improves readability. Do not split calls or redesign APIs solely to satisfy an arbitrary count.
- Group related declarations and keep helpers near their use where practical. Keep names unexported unless another package needs them.
- Avoid dot imports. Use blank imports only when their side effects are needed and clear.
- Use comments to explain intent or non-obvious constraints; remove comments that only repeat the code.

## Strings and conversions

- Use `strconv` for simple conversions and `fmt` for formatting. Use `%q` when quoted string boundaries help diagnose an error.
- Use `+` for simple concatenation and consider `strings.Builder` for repeated construction in a loop.
- Prefer concrete types. Use generics when they make an API clearer or remove meaningful duplication, not by default.
