# FE-5: Show where the answer is in the form

## What it does

The backend sends a breadcrumb with each answer, for example "Section 1: Allgemeine Angaben → Art der Tätigkeit". It tells the user which part of the form the answer is about. The chat shows it as a breadcrumb bar at the top of the bot answer bubble, above the answer text.

## What it does not touch

- Clicking a breadcrumb segment to ask about it (FE-15). Until then the segments are plain text, not buttons.
- The language switch itself (FE-2). The backend writes the breadcrumb in the language of the request; the frontend does not translate it.
- The colour of the answer text. It stays as it is.

## Interface

### `components/BotMessage.tsx`

- New prop `breadcrumb: string | null`, optional. Default `null`.
- When it is a text, the breadcrumb bar is shown inside the bubble, above the answer text. When it is `null`, nothing extra is rendered.

### `components/MessageList.tsx`

- Passes `message.breadcrumb` to `BotMessage`. The welcome message has no breadcrumb.

### `components/icons.tsx`

- New `ArrowRightIcon` for the library icon `arrow-right`, viewBox `0 0 20 12`, with the path data copied from the Figma file. Same props and output as the other icons (FE-8), so the existing icons test covers it.

### Unchanged

- `types.ts`: `ChatReply.breadcrumb` and `Message.breadcrumb` already exist (FE-1).
- `hooks/useChat.ts`: already turns an empty breadcrumb into `null` (FE-1).

## Behaviour (state machine)

No states. The rules:

- The breadcrumb is split at each "→" into segments. Spaces around a segment are removed and empty segments are dropped.
- The backend sends the section number and the section name as one segment ("Section 1: Allgemeine Angaben"); the Figma design shows them as two. So the first segment is also split at its first ": ", and the ": " is not shown. "Section 1: Allgemeine Angaben → Art der Tätigkeit" becomes "Section 1", "Allgemeine Angaben", "Art der Tätigkeit", shown as "Section 1 → Allgemeine Angaben → Art der Tätigkeit". Only the first segment is split this way, because field names further down the path can contain a colon. A first segment without ": " stays one segment.
- The segments are shown in order, with an `arrow-right` icon between two segments. Apart from the splitting, the text is shown as the backend sends it.
- Every segment except the last is blue. The last segment, the place the answer is about, is dark.
- The arrows are hidden from screen readers.
- An empty breadcrumb from the backend shows no bar: no text, no line, no empty space.
- Each bot answer shows its own breadcrumb. Earlier answers keep theirs.

## Preconditions / Postconditions

**Preconditions:** FE-1, FE-2 and FE-8 are done and their tests pass.

**Postconditions:** All earlier tests and the new tests pass. `npm run lint` and `npm run build` pass.

## Edge cases

| Problem | What happens |
|---|---|
| A long breadcrumb that does not fit on one line | The segments wrap onto the next line inside the bubble. |
| A breadcrumb with only the section, for example "Section 1: Allgemeine Angaben" | It becomes "Section 1" (blue), an arrow and "Allgemeine Angaben" (dark), as in the "Breadcrumb Result" frame. |
| A breadcrumb that is one segment with no ": " | It is shown in the last segment's colour, with no arrow. |
| The user switches the language after an answer | Earlier breadcrumbs stay in the language they came in. Only new answers use the new language. |

## Acceptance criteria (Given-When-Then)

**Normal path**

- **Given** the chat is open
- **When** I ask "What should I enter for Art der Tätigkeit?" and the backend answers with the breadcrumb "Section 1: Allgemeine Angaben → Art der Tätigkeit"
- **Then** "Section 1", "Allgemeine Angaben" and "Art der Tätigkeit" are shown in this order at the top of the answer bubble, above a line and the answer text

**Something goes wrong**

- **Given** the chat is open
- **When** I ask a question and the backend answers with an empty breadcrumb
- **Then** only the answer text is shown, with no breadcrumb bar

The German check gets its own smaller test: with DE selected, the request carries `lang: "de"` and the German breadcrumb from the backend is shown.

## Design

The Figma design, frames "Answer Question 1" and "Breadcrumb Result", component "AI Chat Bubble":

| Part | Value |
|---|---|
| Breadcrumb bar | First item inside the bubble, full width, 12px above the answer text (the bubble's existing gap). 2px `neutral-400` line under it, 4px between the segments and the line. |
| Segment row | Wraps onto more lines when it does not fit. Drop shadow `0 1px 4px rgba(0, 0, 0, 0.25)` on the row. |
| Segment | The "Link" type of the Figma "Button" component, default state only, since the segments are not clickable yet (FE-15). 8px padding on all sides, H5 Regular (18px, line height 1.45). `blue-600` for every segment but the last, `neutral-900` for the last. |
| Arrow | `arrow-right` icon, 20px wide, black, between two segments. |

Both frames hide the bar on the welcome message, which has no breadcrumb. That matches the rule for an empty breadcrumb.
