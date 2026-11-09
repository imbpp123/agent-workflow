# Testify in Go tests

Follow the project's test style. Check its Testify version before using an API. Use `testify/mock` when interactions are part of the contract. See [go-testing](../SKILL.md) for the choice between a fake and a mock.

## Assertions

- Use `require` when a failed precondition makes later checks unsafe or meaningless. Use `assert` for independent checks. Call `require` only from the test goroutine.
- In equality checks, put the expected value before the actual value. Use `ErrorIs` or `ErrorAs` for wrapped errors. `Equal` compares values behind pointers. Use `Same` when pointer identity matters.
- Choose checks that match the contract. Use `ElementsMatch` for unordered collections or `JSONEq` for JSON structure. Check that the project's Testify version has the API.
- Prefer explicit signals for asynchronous behavior. Bound polling with a timeout when it is needed. In an `EventuallyWithT` callback, stop after a failed prerequisite before using its result.

## Mocks

Embed `mock.Mock` and implement the interface. Set expectations before the operation. Check them after the operation and its workers finish:

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

Check expected interactions with `AssertExpectations(t)`. Use `AssertCalled`, `AssertNotCalled`, or `AssertNumberOfCalls` when a specific call or count is part of the contract. Pass the same number of arguments as the mocked method. Expectations do not check call order by default.

- Match arguments precisely when they matter. Use `mock.Anything` for irrelevant values and `mock.IsType` for a type. `mock.MatchedBy` takes a function with one argument and a `bool` result. Use string type names only when needed.
- Use `Once` or `Times` for required call counts. Use `Maybe` for an optional call and `Run` for a needed side effect. Successive one-time expectations can model retries with different return values.
- `Unset` supports expectations with static arguments. It can remove several matching handlers. Prefer a fresh mock for each test case.
- Do not attach `Mock.Test(t)` to a mock called from another goroutine. Wait for workers before assertions. A pointer argument may change after a call. Later call checks can then give misleading results. Capture the needed value at call time.

## Suites

Use `testify/suite` when shared setup and cleanup make tests clearer. Start the suite with `suite.Run`. Keep each test's state in `SetupTest`. Do not use parallel tests in a Testify suite. Plain subtests are often enough.

For API details, see the official [assert](https://pkg.go.dev/github.com/stretchr/testify/assert), [mock](https://pkg.go.dev/github.com/stretchr/testify/mock), and [suite](https://pkg.go.dev/github.com/stretchr/testify/suite) documentation.
