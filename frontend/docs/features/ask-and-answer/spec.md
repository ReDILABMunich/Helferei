# FE-1: Ask a question in English and read the answer

## What it does

The user opens Atlas, types a question in English and sends it with Enter or the send button. The question shows as a user bubble, a loading indicator shows while the backend works, and the answer shows as a bot bubble with markdown formatting. Follow-up questions continue the same conversation. If the request fails, an error message shows. The screen has no styling yet.

## What it does not touch

- The backend. The `/chat` contract stays as it is.
- German and the language dropdown (FE-2). Every request sends `lang: "en"`.
- The retry button (FE-3). The error message has no button yet.
- The character counter (FE-6). The input has no counter yet.
- Matching the Figma design (FE-9).
- The "New chat" button (FE-4), the breadcrumb line (FE-5), the other screen sizes (FE-7), the icons (FE-8).

## Interface

### `api/chat.ts`

```ts
sendChat(request: ChatRequest): Promise<ChatReply>
```

- In: `{ message, session_id, lang }`. `session_id` is `null` on the first question.
- Out: `{ answer, session_id, breadcrumb }`.
- Throws when the network fails or the backend returns a status that is not 2xx.

### `hooks/useChat.ts`

```ts
useChat(): { messages: Message[]; status: ConversationStatus; send(text: string): void }
```

- `messages`: the user's questions and the bot's answers, oldest first. The welcome message is not in this list (decision 001).
- `status`: `"idle" | "sending" | "failed"`.
- `send(text)`: sends a question. When it is ignored: see Behaviour.

## Behaviour (state machine)

| From | Event | To | What happens |
|---|---|---|---|
| idle | send (non-empty text) | sending | Question added to `messages`, request sent |
| sending | reply arrives | idle | Answer added to `messages` |
| sending | request fails | failed | Error message shown |
| failed | send (non-empty text) | sending | Error message hidden, question added, request sent |
| sending | send (any text) | sending | Ignored |
| idle or failed | send (empty or only spaces) | unchanged | Ignored |

The loading indicator shows exactly while `status` is `"sending"`.

## Preconditions / Postconditions

**Preconditions:** a send is accepted only from `idle` or `failed`, with text that is not empty. Behaviour shows every case.

**Postconditions:**

- Every accepted send makes exactly one request. It carries the current `sessionId`, which is `null` until the first answer arrives.
- After a reply, `sessionId` is the one from that reply.
- A failed request never removes the question from `messages` and never changes `sessionId`, so the next question continues the same conversation.

## Edge cases

Request failures (network down, backend asleep, an error status), double sends (holding Enter, or Enter and then a click) and empty messages are covered in Behaviour. Other edge cases:

| Problem | What happens |
|---|---|
| Backend answer uses "•" for bullet points | Converted to a markdown list before rendering. |

## Acceptance criteria (Given-When-Then)

**Normal path**

- **Given** the chat is open and no question has been asked yet
- **When** I type "What is a Steuernummer?" and press Enter
- **Then** my question appears as a user bubble and a loading indicator shows
- **And when** the backend answers
- **Then** the answer appears as a bot bubble, the loading indicator disappears, and my next question is sent with the `session_id` from that answer

**Something goes wrong**

- **Given** I have asked one question and got an answer
- **When** I ask a second question and the backend returns an error
- **Then** an error message appears, the loading indicator disappears, and my second question stays visible
- **And when** I ask a third question
- **Then** the error message disappears and the request is sent with the same `session_id` as before

## Design

No styling in this ticket. FE-9 matches the screen to the Figma design.
