# Testify in Go tests

Follow the project's existing conventions and check its testify version before using an API. Test behavior, not implementation details. Prefer a simple fake or stub when call expectations add no value; use `testify/mock` when the interaction itself matters.

## Assertions

- Use `require` for a failed precondition that makes the rest unsafe or meaningless, and `assert` for independent checks. Call `require` only from the goroutine running the test.
- In equality assertions, put the expected value before the actual value. Use `ErrorIs` or `ErrorAs` for wrapped errors. `Equal` compares pointed-to values; use `Same` when pointer identity matters.
- Choose assertions that describe the contract: for example, `ElementsMatch` for unordered collections or `JSONEq` for JSON structure. Check API availability in the project's version.
- For asynchronous behavior, prefer explicit synchronization. When polling is needed, bound it with a timeout. In an `EventuallyWithT` callback, stop after a failed prerequisite before using its result.

## Mocks

Embed `mock.Mock`, implement the interface, configure expectations, and verify them after the operation and any workers have finished:

```go
type Sender interface {
    Send(context.Context, string) error
}

func Notify(ctx context.Context, sender Sender, to string) error {
    return sender.Send(ctx, to)
}

type MockSender struct{ mock.Mock }

func (m *MockSender) Send(ctx context.Context, to string) error {
    return m.Called(ctx, to).Error(0)
}

func TestNotify(t *testing.T) {
    sender := new(MockSender)
    sender.On("Send", mock.Anything, "buyer@example.com").Return(nil).Once()

    err := Notify(context.Background(), sender, "buyer@example.com")

    assert.NoError(t, err)
    sender.AssertExpectations(t)
}
```

Verify expected interactions with `AssertExpectations(t)`; use `AssertCalled`, `AssertNotCalled`, or `AssertNumberOfCalls` when the specific call or count is part of the contract. Pass the same number of arguments as the mocked method. Expectations are not checked in call order by default.

- Match arguments precisely when they matter. Use `mock.Anything` for irrelevant values, `mock.IsType` for a type, or `mock.MatchedBy` for a predicate with one argument and a `bool` result. Avoid string type names unless necessary.
- Use `Once` or `Times` for required call counts, `Maybe` for an optional call, and `Run` for a needed side effect. Sequential one-time expectations can model retries with different return values.
- `Unset` supports expectations with static arguments and can remove multiple matching handlers. Prefer a fresh mock for each test case.
- Do not attach `Mock.Test(t)` to a mock called from another goroutine. Wait for workers before assertions. If a pointer argument changes after a call, later call assertions can report misleading results; capture the required value at call time instead.

## Suites

Use `testify/suite` only when shared setup and teardown improve clarity. Start the suite with `suite.Run`, keep per-test state in `SetupTest`, and do not use parallel tests in a testify suite. Plain subtests are often sufficient.

For API details, see the official [assert](https://pkg.go.dev/github.com/stretchr/testify/assert), [mock](https://pkg.go.dev/github.com/stretchr/testify/mock), and [suite](https://pkg.go.dev/github.com/stretchr/testify/suite) documentation.
