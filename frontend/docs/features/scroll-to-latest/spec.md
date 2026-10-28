# FE-14: See the latest message without scrolling

## What it does

The chat scrolls down by itself, so the newest thing in the chat is always visible: the user's question with the loading indicator, the answer, or the error message with the "Try again" button.

## What it does not touch

- A "scroll to bottom" button.
- Keeping the position when the user scrolls up while waiting for an answer. The chat still scrolls down when the answer arrives.
- Smooth scrolling. The chat jumps to the end.
- The backend.

## Interface

### `App.tsx`

- An empty marker element after the loading indicator and the error message, as the last element in the scrolling area.
- After every render where `messages` or `status` changed, the marker is scrolled into view with `scrollIntoView({ block: "end" })`.

No new props, hooks or content.

## Behaviour (state machine)

The scrolling follows the states of FE-1 and FE-3. It does not add new states.

| From | Event | To | What happens |
|---|---|---|---|
| idle | Send a question | sending | The question and the loading indicator are added, then the chat scrolls to the end. |
| sending | Answer arrives | idle | The answer is added, then the chat scrolls to the end. |
| sending | Request fails | failed | The error message is shown, then the chat scrolls to the end. |
| failed | Click "Try again" | sending | The loading indicator replaces the error message, then the chat scrolls to the end. |

## Preconditions / Postconditions

**Preconditions:** FE-13 is done and its tests pass.

**Postconditions:** All earlier tests and the new tests pass. `npm run lint` and `npm run build` pass.

## Edge cases

| Problem | What happens |
|---|---|
| The user switches the language | `messages` and `status` do not change, so the chat does not scroll. |
| The user starts a new chat | `messages` becomes empty, so the chat scrolls to the end, which is the welcome message. Nothing visible moves. |
| The first render | The chat scrolls to the end once. Only the welcome message is there, so nothing visible moves. |

## Acceptance criteria (Given-When-Then)

**Normal path**

- **Given** the chat is open
- **When** I send a question and the answer arrives
- **Then** the chat scrolls to the end after the question is added, and again after the answer is added

**Something goes wrong**

- **Given** the chat is open
- **When** I send a question and the request fails
- **Then** the chat scrolls to the end after the error message is shown

## Design

Nothing new to measure in the Figma design. The space below the last message is the existing gap of the message list.
