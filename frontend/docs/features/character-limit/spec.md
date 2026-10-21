# FE-6: See the character limit while typing

## What it does

A question can be at most 800 characters long, the limit in the Figma design. A counter under the input shows how many characters the user has typed out of 800. Over the limit, the input shows an error message and the send button is disabled. When the user deletes back to 800 or fewer, sending works again.

## What it does not touch

- A limit check on the backend.
- The error when the user sends an empty box, and an input that grows with the text. Both are in the Figma design but are left for a new ticket.
- The send button's hover and pressing states. They are part of the open note about the send button states.
- The icons (FE-8). Until FE-8, the warning icon is a simple placeholder, as in the error message.

## Interface

### `components/MessageInput.tsx`

- `MAX_LENGTH = 800`: the limit, a constant in the component. It is a number, not interface text, so it does not live in `content/`.
- Props are unchanged: `{ content, onSend, sending }`.
- The counter shows `/800` when the box is empty, and `<count>/800` otherwise, where `<count>` is the length of the text in the box.
- Over the limit, the text box has `aria-invalid="true"`, so screen readers announce the error, and the send button is `disabled`.

### `content/`

- `tooLong`: the error message. English "Your message is too long. Please keep it under 800 characters", German "Ihre Nachricht ist zu lang. Bitte halten Sie sie unter 800 Zeichen."

## Behaviour (state machine)

| From | Event | To | What happens |
|---|---|---|---|
| within limit | Type or paste, length becomes more than 800 | over limit | The counter shows the new count, for example `900/800`. The error message is shown and the send button is disabled. |
| over limit | Click send or press Enter | over limit | Nothing is sent. The text stays in the box. |
| over limit | Delete, length becomes 800 or less | within limit | The error message is removed. Sending works again. |
| within limit | Type or delete | within limit | The counter shows the new count. |
| within limit | Send | within limit | As in FE-1. The box is cleared and the counter shows `/800`. |

"Within limit" means 0 to 800 characters, so exactly 800 can be sent.

## Preconditions / Postconditions

**Preconditions:** FE-1 is done and its tests pass.

**Postconditions:** All earlier tests and the new tests pass. `npm run lint` and `npm run build` pass.

## Edge cases

| Problem | What happens |
|---|---|
| The text is only spaces and over 800 | It is not sent, by both rules: empty text (FE-1) and the limit. The counter counts the spaces. |
| An emoji or other special character | It counts as JavaScript counts string length, so some emoji count as 2. The backend has no limit, so this only changes the number shown. |
| The user switches the language while over the limit | The text stays. The error message is shown in the new language. |

## Acceptance criteria (Given-When-Then)

**Normal path**

- **Given** the chat is open
- **When** I type "What is a Steuernummer?"
- **Then** the counter shows `23/800`

**Something goes wrong**

- **Given** the chat is open
- **When** I paste 900 characters and click send
- **Then** the counter shows `900/800`, the error message is shown, and nothing is sent

## Design

The Figma design, component "Input Field", states "Empty State / Default", "Filled State / Short Question" and "Filled State / Error (Maximum character limit)":

| Part | What to measure |
|---|---|
| Counter | Position, font, colour when empty, colour while typing, colour over the limit |
| Input over the limit | Border colour, the line above the bottom row |
| Error message | Warning icon size and colour, font, colour, space to the counter |
| Send button over the limit | Background and icon colour of the disabled button |
