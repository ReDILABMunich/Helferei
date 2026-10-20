# FE-3: Try again after an error

## What it does

When a question fails, the error message has a "Try again" button. Clicking it sends the same question again, with the same session, so the user does not have to type it again. The question stays in the chat once.

## What it does not touch

- Retrying automatically, or a time limit for requests.
- What happens when the user types a new question instead of clicking "Try again". As in FE-1, the new question is sent and the failed question stays without an answer.
- The icons (FE-8). Until FE-8, the refresh icon on the button is a simple placeholder, like the warning icon.
- The backend.

## Interface

### `hooks/useChat.ts`

```ts
useChat(lang: Language): {
  messages: Message[];
  status: ConversationStatus;
  send(text: string): void;
  retry(): void;
}
```

- `send` remembers the question it sends. Everything else is as in FE-2.
- `retry` sends the remembered question again. It does not add a user message.

### `content/`

- `error.retry`: the button text. English "Try again", German "Erneut versuchen".

### Components

- `ErrorMessage({ content, onRetry })`: shows the button and calls `onRetry` when it is clicked.

## Behaviour (state machine)

| From | Event | To | What happens |
|---|---|---|---|
| failed | Click "Try again" | sending | The last question is sent again with the current session id and the current language. No new user message. The error message is replaced by the loading indicator. |
| sending | Answer arrives | idle | The answer is added, as in FE-1. |
| sending | Request fails | failed | The error message with the button is shown again. |

All other transitions are as in FE-1.

## Preconditions / Postconditions

**Preconditions:** FE-2 is done and its tests pass.

**Postconditions:** All earlier tests and the new tests pass. `npm run lint` and `npm run build` pass.

## Edge cases

| Problem | What happens |
|---|---|
| The first question of the conversation fails | There is no session yet, so the retry is sent with `session_id: null`, the same as the first attempt. |
| The user switches the language after the error, then clicks "Try again" | The question is sent with the new language, the same rule as in FE-2: a request uses the language selected when it is sent. |
| The user clicks "Try again" twice quickly | Only one request is sent, the same block as a fast second send in FE-1. |

## Acceptance criteria (Given-When-Then)

**Normal path**

- **Given** I asked a question and the request failed
- **When** I click "Try again"
- **Then** the same question is sent again with the same session id, the answer appears, and my question is shown only once

**Something goes wrong**

- **Given** I asked a question and the request failed
- **When** I click "Try again" and the request fails again
- **Then** the error message with the "Try again" button is shown again, and my question is still shown only once

## Design

The Figma design, component "AI Chat Bubble", variant "Error Message":

| Part | What to measure |
|---|---|
| "Try again" button | Size, padding, border, radius, background, shadow, font, space between text and icon |
| Refresh icon | Size and colour |
| Error message | Space between the text and the button |
