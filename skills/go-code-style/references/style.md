# Go style reference

## Names

- Use short, clear names. Use standard acronyms, as in `HTTPServer`, `userID`, and `URL`.
- Keep package names short and lowercase. Avoid repeating the package name in exported names.

### Repositories

- Name repository variables, fields, and parameters after the stored domain entity, in plural form. Use `bankAccounts` for a `BankAccountRepository` and `orders` for an `OrderRepository`.
- When two repositories store the same entity, add their roles. Keep the plural entity name, as in `sourceAccounts` and `targetAccounts`.
- Start method names with a verb, such as `GetByID`, `List`, or `Save`. Omit the entity name when the repository already makes it clear.
- Keep the entity name when it helps distinguish the result. Use `ListTransactions` when an account repository returns transactions. Keep enough of the name to make the call clear.
- Keep useful filter details, as in `ListByAccountID` on a transaction repository.
- Give result collections their own names, such as `accountList`. Use a name such as `activeAccounts` only when the result contains only active accounts.

For a repository that stores bank accounts, use these names for the interface, service field, and constructor parameter.

```go
type BankAccountRepository interface {
	GetByID(ctx context.Context, id string) (BankAccount, error)
	List(ctx context.Context) ([]BankAccount, error)
	Save(ctx context.Context, account BankAccount) error
}

type accountService struct {
	bankAccounts BankAccountRepository
}

func newAccountService(bankAccounts BankAccountRepository) *accountService {
	return &accountService{
		bankAccounts: bankAccounts,
	}
}
```

At the call site, use `bankAccounts.GetByID(ctx, accountID)` and `accountList, err := bankAccounts.List(ctx)`.

## Interfaces, errors, and resources

- Keep interfaces small. Put them near the code that uses them when this helps. Preserve public APIs unless the task requires a change.
- Handle errors and add the operation context. Preserve the error chain with `%w` when callers need `errors.Is` or `errors.As`.
- When a boundary must hide infrastructure types, return the error defined by that boundary's contract. Keep safe diagnostics inside the responsible layer.
- Avoid logging the same failure at several layers. For logging decisions, read [Go observability](../../go-observability/SKILL.md).
- Use `panic` only for programming errors that cannot be handled safely.
- Pass the caller's context when cancellation or deadlines are needed. Store it in a struct only when an existing API requires it.
- Release resources on every path. Use `defer` when it makes ownership clear.

For layer boundaries and ports in a Clean Architecture project, read [Go Clean Architecture](../../go-clean-architecture/SKILL.md).

## Declarations and values

- Use `:=` for local values when it makes the code clearer. Use `var` when the zero value is useful or the type should be explicit.
- A nil slice is valid. Follow the API contract when choosing a nil or empty slice, especially for JSON. Initialize a map before writing to it.
- Use named fields in struct literals when they make the code clear or protect against field changes. Follow the existing use of that type.
- Pass simple values such as `string`, `int`, `bool`, and `time.Time` by value unless a pointer has a clear purpose. A copy can still refer to shared data.
- Use a pointer parameter when the function must change or share the original value, avoid an unsafe copy, or use `nil` for an optional value. Measure the cost of copying before using a pointer for speed.
- Maps and slices can share data even when passed by value. Do not copy a struct that contains a `sync.Mutex` after the mutex has been used.

For other synchronization values and shared state, read [Go concurrency](../../go-concurrency/SKILL.md).

```go
func FormatUser(name string, createdAt time.Time) string
func SetDefaults(cfg *Config) // changes cfg
func UpdateName(ctx context.Context, name *string) error // nil means unchanged
```

These rules apply to function parameters. Choose method receivers based on the type and its methods. Use the same receiver kind where practical.

## Control flow and functions

- Handle errors and special cases early when this reduces nesting. Omit `else` after a branch that exits.
- Use `switch` when it makes alternatives clearer. Give complex conditions names only when the names explain their purpose. Keep short-circuit evaluation and side effects.
- Keep functions focused. Prefer a small number of parameters. Add a struct only when the values belong together or it improves the API.
- Put `context.Context` first when a function needs it. Write the return values explicitly when a naked return would be unclear.
- Prefer `range` when it makes iteration clearer. Use language features supported by the project's Go version.

Name the cheap checks and leave a later check in the condition so it runs only when needed.

```go
isAdmin := user.Role == RoleAdmin
isOwner := resource.OwnerID == user.ID
if isAdmin || isOwner || hasPermission(user, resource) {
	allow()
}
```

Moving `hasPermission` into a variable before the condition would call it even when an earlier check succeeds. Keep checks that depend on earlier guards in the right order, such as a field access after a nil check.

## Layout and organization

- Break long lines where it makes the code easier to read. Do not split calls or redesign APIs only to meet a line length or parameter count without a project rule.
- Group related declarations. Keep helpers near the code that uses them where practical. Keep names unexported unless another package needs them.
- Avoid dot imports. Use blank imports only when their side effects are needed and clear.
- Use comments to explain intent or a constraint that the code does not show. Remove comments that only repeat the code.

## Strings and conversions

- Use `strconv` for simple conversions and `fmt` for formatting. Use `%q` when quotes around the input make errors easier to understand.
- Use `+` for simple concatenation and consider `strings.Builder` for repeated construction in a loop.
- Prefer concrete types. Use generics when they make an API clearer or remove repeated code that is hard to maintain.
