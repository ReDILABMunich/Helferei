# FE-15: Go to a part of the form by clicking the breadcrumb

## What it does

The breadcrumb at the top of a bot answer (FE-5) becomes clickable. Every segment except the last is a button. Clicking a segment sends the path up to and including that segment as a new question, in the same conversation. The path shows as the user's bubble, and the answer explains that part of the form, as in the "Breadcrumb Result" frame of the Figma design.

## What it does not touch

- The backend. It already moves to a place in the form when it receives a path such as "Section 1 → Allgemeine Angaben".
- Clicking the last segment. It stays plain text.
- Keyboard focus styles.
- How the breadcrumb is split into segments. That stays as in FE-5.

## Interface

Components cannot call the backend (decision 002). So a click on a segment calls `send` from `useChat`, the same function the input box uses.

- `BotMessage` gets a new prop, `onSegmentClick`. A click calls it with the path of the segment, for example "Section 1 → Allgemeine Angaben".
- `App` gives `send` to `MessageList`, and `MessageList` gives it to each `BotMessage` as `onSegmentClick`.
- `useChat` does not change. `send` already adds the user bubble, keeps the `session_id` and ignores a click while an answer is loading.

## Behaviour (state machine)

No new states. The rules:

- Every segment except the last is a button. The last segment is plain text.
- Clicking a segment sends its path, for example "Section 1 → Allgemeine Angaben" for "Allgemeine Angaben" in "Section 1 → Allgemeine Angaben → Art der Tätigkeit". Clicking "Section 1" sends "Section 1".
- The path is sent like a typed question: it shows as the user's bubble, the request carries the same `session_id` and the selected language, and the answer shows with its own breadcrumb.
- While an answer is loading, a click sends nothing and adds no bubble.
- Segments in earlier answers stay clickable.

## Preconditions / Postconditions

**Preconditions:** FE-5 and FE-11 are done and their tests pass.

**Postconditions:** All earlier tests and the new tests pass. `npm run lint` and `npm run build` pass.

## Edge cases

| Problem | What happens |
|---|---|
| A breadcrumb with only one segment | It is the last segment, so there is no button. |
| The last request failed and the error is showing | A click sends the path as a new question, like typing one. |
| German is selected | The path is built from the German segments, for example "Abschnitt 1 → Allgemeine Angaben". The frontend does not translate it. |
| Text is typed in the input box when a segment is clicked | The typed text stays in the box. Only the path is sent. |

## Acceptance criteria (Given-When-Then)

**Normal path**

- **Given** the answer to "What should I enter for Art der Tätigkeit?" shows the breadcrumb "Section 1 → Allgemeine Angaben → Art der Tätigkeit"
- **When** I click "Allgemeine Angaben"
- **Then** "Section 1 → Allgemeine Angaben" shows as my user bubble, it is sent with the same `session_id`, and the answer shows with its own breadcrumb

**Something goes wrong**

- **Given** I asked a question and its answer is still loading, and an earlier answer shows a breadcrumb
- **When** I click a segment of that breadcrumb
- **Then** nothing is sent and no user bubble is added

Smaller tests: the last segment is not a button, and clicking "Section 1" sends "Section 1".

## Design

The Figma design, frames "Answer Question 1" and "Breadcrumb Result", and the "Button" component:

| Part | Value |
|---|---|
| Clickable segment | "Link" type. Default: `blue-600`, as in FE-5. Hover: `brand-500`. While pressing: `blue-900`. Pointer cursor on hover. |
| Last segment | "Unlinked" type: `neutral-900`, no hover or pressed state. |
| Size and spacing | Unchanged from FE-5: 8px padding, H5 Regular. |

Hover and pressed colours cannot be measured in jsdom, so they are checked by eye in the browser.
