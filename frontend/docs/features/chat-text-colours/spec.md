# FE-13: Read the chat and the hint in the right text colours and bubble corners

## What it does

The text in the chat bubbles becomes `neutral-900`, as in the Figma design. In a bot answer, the German field names become `blue-900`, so users can find them and copy them into the tax form. The bot answer bubble gets the 24px corners of the Figma "AI Chat" layer.

## What it does not touch

- The hint strip. Its text stays `blue-900`, because the Figma design was changed to this colour after the ticket was written.
- The breadcrumb (FE-5, FE-15).
- The backend and how the agent writes its answers.
- The colour of the other lines in the answer, such as the navigation tip at the end.

## Interface

- New function `fieldName(line: string, first: boolean): string | null` in `BotMessage`. It gets one line of the answer text, and whether it is the first line. It returns the German field name in the line, or `null` if there is none.
- `BotMessage` shows the returned name in `blue-900`. The rest of the line keeps its colour.
- No new props.

## Behaviour (state machine)

No new states. The rules:

- The text in the bot and user bubbles is `neutral-900`.
- A list item with " · ": the field name is the text before the first " · ". Example: "• Geburtsdatum · Date of Birth — date of birth" gives "Geburtsdatum".
- A list item without " · " but with " — ": the field name is the text before the first " — ". This is how the agent writes list items in German. Example: "• Geburtsdatum — Ihr Geburtsdatum" gives "Geburtsdatum".
- The first line of the answer, if it starts with a single quote, or with "Section N '" or "Abschnitt N '": the field name is the text inside the first pair of single quotes. Example: "Section 9 'Betriebsstätten' · Business Premises — asks about..." gives "Betriebsstätten". This works for English and German answers.
- Every other line has no field name.

## Preconditions / Postconditions

**Preconditions:** FE-9 is done and its tests pass.

**Postconditions:** All earlier tests and the new tests pass. `npm run lint` and `npm run build` pass.

## Edge cases

| Problem | What happens |
|---|---|
| A list item has neither " · " nor " — " | No field name. The line keeps its colour. |
| The first line has no single quotes | No field name on the first line. |
| The first line quotes the user's words, for example "I found several matching 'gebusdatum' in:" | It does not start with a quote, "Section N '" or "Abschnitt N '", so nothing is blue. |
| A field name contains " - ", for example "Adresse - nur anzugeben, falls ..." | The whole name is blue. Only " · " and " — " end a name, " - " does not. |
| The description after the name also contains " · " or " — " | Only the first one counts, the name ends there. |
| The navigation tip at the end has quotes, for example 'Geburtsdatum' | It is not the first line and not a list item, so nothing is blue. |
| The welcome message | It has no list items with " · " or " — ", and its first line has no single quotes, so nothing is blue. |

## Acceptance criteria (Given-When-Then)

**Normal path**

- **Given** I asked about Section 9
- **When** the answer shows "Section 9 'Betriebsstätten' · Business Premises — asks about..." and the list item "• Bezeichnung der Betriebsstätte · Name/Description of Business Premise — ..."
- **Then** "Betriebsstätten" and "Bezeichnung der Betriebsstätte" are `blue-900`, and the rest of the answer is `neutral-900`

**Something goes wrong**

- **Given** I asked a question
- **When** the answer has a list item with neither " · " nor " — "
- **Then** nothing in that item is `blue-900`, and the answer shows as before

Smaller tests: one per rule in Behaviour and per row in Edge cases, on `fieldName`.

## Design

The Figma design, "AI Chat" layer and the "Chat Thread" frame:

| Part | Value |
|---|---|
| Bot and user bubble text | `neutral-900` (#1A1A1A) |
| German field name | `blue-900` |
| Bot answer bubble corners | 24px top left, top right and bottom right, 0 bottom left |

Colours and corners cannot be measured in jsdom, so they are measured in the browser with Playwright.
