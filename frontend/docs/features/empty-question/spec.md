# FE-10: See an error for an empty question and a growing input

## What it does

When the user sends an empty box, the input shows an error under the text box instead of doing nothing. The error goes away as soon as the user types. The text box also grows taller as the question gets longer, and the text wraps onto new lines.

## What it does not touch

- The character limit and its error (FE-6). Its rules stay as they are.
- The send button states (FE-11).

## Interface

### `components/MessageInput.tsx`

- Props are unchanged: `{ content, onSend, sending }`.
- New state `empty`: `true` after the user tries to send an empty box, `false` again when the text changes.
- While `empty` is `true`, the text box has `aria-invalid="true"` and the error is shown in the same place as the FE-6 error.
- The text box grows with its text. It has no maximum height, as in the Figma design.

### `content/`

- `empty`: the error message. English "Please type a question before sending", German "Bitte geben Sie eine Frage ein, bevor Sie senden."

## Behaviour (state machine)

| From | Event | To | What happens |
|---|---|---|---|
| no error | Click send or press Enter with an empty box | empty error | Nothing is sent. The border turns to the error colour and the error message is shown. |
| empty error | Type a character | no error | The error message is removed and the border goes back to normal. |
| empty error | Click send or press Enter again | empty error | Nothing changes. |

"Empty" means what it means in FE-1: no text, or only spaces and line breaks.

## Preconditions / Postconditions

**Preconditions:** FE-1 and FE-6 are done and their tests pass.

**Postconditions:** All earlier tests and the new tests pass. `npm run lint` and `npm run build` pass.

## Edge cases

| Problem | What happens |
|---|---|
| The box has only spaces | It counts as empty, so the empty error is shown. |

## Acceptance criteria (Given-When-Then)

**Normal path**

- **Given** I tried to send an empty box and the error is shown
- **When** I type "W"
- **Then** the error message is gone and the text box is no longer marked as invalid

**Something goes wrong**

- **Given** the chat is open and the box is empty
- **When** I click send
- **Then** "Please type a question before sending" is shown, the text box is marked as invalid, and nothing is sent

The growing input is checked by eye in the browser. jsdom does not measure heights, so it has no test.

## Design

The Figma design, component "Input Field", state "Empty Error":

| Part | Value |
|---|---|
| Input border | 3px `red-500` |
| Error row | 12px space above it, no line above it (unlike the FE-6 error) |
| Error message | Caution icon 28px wide, 8px gap to the text, 12px from the left, body text, `red-600` |
| Counter | `/800` in `neutral-300`, as in the empty state |

State "Filled Multiline": each line of text is 24px high, so 5 lines make the text 120px high. State "Limit Reached" shows 11 lines without scrolling.
