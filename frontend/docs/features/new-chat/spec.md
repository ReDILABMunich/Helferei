# FE-4: Start a new conversation

## What it does

A "New chat" button in the header, next to the language dropdown, opens a confirmation dialog. When the user confirms, the conversation is cleared: only the welcome message is left, and the next question starts a new session, so the agent does not remember the earlier conversation. When the user cancels, nothing changes.

## What it does not touch

- Saving or showing old conversations.
- The backend. A request with `session_id: null` already starts a new session there, so no reset endpoint is needed.
- The icons (FE-8). Until FE-8, the "doc-add" icon on the button, the warning icon and the close icon in the dialog are simple placeholders.
- Other screen sizes (FE-7).

## Interface

### `hooks/useChat.ts`

```ts
useChat(lang: Language): {
  messages: Message[];
  status: ConversationStatus;
  send(text: string): void;
  retry(): void;
  reset(): void;
}
```

- `reset` clears the messages, sets the status to `idle`, and forgets the session id and the last question. The next `send` is sent with `session_id: null`.
- Everything else is as in FE-3.

### `content/`

| Key | English | German |
|---|---|---|
| `newChat.button` | New chat | Neuer Chat |
| `newChat.title` | Are you sure you want to start a new conversation? | Möchten Sie wirklich eine neue Unterhaltung beginnen? |
| `newChat.body` | This will clear your current conversation. | Dadurch wird Ihre aktuelle Unterhaltung gelöscht. |
| `newChat.cancel` | Cancel | Abbrechen |
| `newChat.confirm` | Yes, Reset | Ja, zurücksetzen |
| `newChat.close` | Close | Schließen |

The header button has no visible text, only an icon. `newChat.button` is its `aria-label`. `newChat.close` is the `aria-label` of the close icon in the dialog.

### Components

- `AppHeader({ content, onLanguageChange, onNewChat })`: shows the "New chat" button after the language dropdown and calls `onNewChat` when it is clicked.
- `NewChatDialog({ content, onConfirm, onCancel })`: the dialog. It has `role="dialog"`, `aria-modal="true"`, and the title as its name. "Yes, Reset" calls `onConfirm`. "Cancel", the close icon, the Escape key and a click on the dimmed background call `onCancel`. When it opens, the focus is on "Cancel".

### `App.tsx`

- Holds whether the dialog is open.
- On confirm, it closes the dialog, calls `reset`, and clears the text box. The text box is cleared by giving `MessageInput` a new `key`, so its state starts again.

## Behaviour (state machine)

The dialog:

| From | Event | To | What happens |
|---|---|---|---|
| closed | Click "New chat" | open | The dialog is shown over a dimmed page. |
| open | Click "Cancel", click the close icon, press Escape, or click the dimmed background | closed | Nothing else changes: the messages, the session, the status, the language and the text box stay as they were. |
| open | Click "Yes, Reset" | closed | The conversation is cleared, see below. |

The conversation on "Yes, Reset":

| From | Event | To | What happens |
|---|---|---|---|
| idle | Reset | idle | The messages, the session id and the last question are forgotten. The text box is cleared. Only the welcome message is shown. The language stays. |
| sending | Reset | idle | As above. The loading indicator is removed. The answer to the open request is ignored when it arrives, and a new question can be sent at once. |
| failed | Reset | idle | As above. The error message is removed. |

## Preconditions / Postconditions

**Preconditions:** FE-1 is done and its tests pass.

**Postconditions:** All earlier tests and the new tests pass. `npm run lint` and `npm run build` pass.

## Edge cases

| Problem | What happens |
|---|---|
| The user clicks "New chat" when the chat is already empty | The dialog opens as usual. Confirming changes nothing that can be seen. |
| The open request fails after a reset | The failure is ignored. No error message is shown in the new conversation. |
| The user switches the language while the dialog is open | The dialog is shown in the new language. |

## Acceptance criteria (Given-When-Then)

**Normal path**

- **Given** I asked a question and got an answer
- **When** I click "New chat" and confirm with "Yes, Reset"
- **Then** only the welcome message is left, and my next question is sent without the earlier session id

**Something goes wrong**

- **Given** I asked a question and got an answer
- **When** I click "New chat" and then "Cancel"
- **Then** the dialog closes, my question and the answer are still shown, and my next question is sent with the same session id

## Design

The Figma design, screens "New Chat Confirmation" and "Reset and start a New Chat", and the "doc-add" button in the header (28 × 33.52 px):

| Part | What to measure |
|---|---|
| "New chat" button | Size, icon size and colour, space to the language dropdown |
| Dimmed background | Colour and opacity |
| Dialog | Width, padding, background, radius, shadow |
| Warning icon | Size and colour, space to the text |
| Title and body | Font, size, colour, space between them |
| Close icon | Size, colour, position |
| "Cancel" and "Yes, Reset" buttons | Size, padding, border, radius, background, font, space between them, hover and pressing states |
