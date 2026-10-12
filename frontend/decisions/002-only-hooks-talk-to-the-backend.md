# 002: Only hooks talk to the backend

## Context

Several parts of the interface cause a request to the backend: the send button, the Enter key, and the retry button (Ticket 3). Every request must carry the current `session_id`. Without it, the backend treats the request as a new conversation and the agent silently forgets the earlier questions. There is no error; the user only notices that the answers no longer make sense.

A question must also be sent only once, even when Enter is held down or Enter is followed by a click (Ticket 1).

If each component sent its own requests, each one would have to add the `session_id` and guard against double sending. One missed spot breaks the conversation without any visible error.

## Decision

Components never import `api` or `hooks`. They get data and callbacks (for example `onSend`, `onRetry`) through props. Only the `hooks` layer calls `api`. dependency-cruiser checks this rule on every lint run.

## Consequences

- The `session_id` and the double-send guard live in one place.
- Components can be tested without a backend: the test passes props and checks what is drawn.
- `App.tsx` has more to pass down, because it connects the hook to the components.

## When to reconsider

- If `App.tsx` becomes hard to read because it passes too many props through several levels of components.
- If the app grows to more than one screen that needs the conversation state.
