# FE-2: Switch the chat to German

## What it does

A language dropdown in the header lets the user switch between English and German. All interface text changes to the selected language, and every question is sent with that language, so the agent answers in it.

## What it does not touch

- A third language. Only the way to add one is prepared.
- Detecting the language automatically, or remembering the choice after a page reload.
- The backend. It already accepts `lang: "en" | "de"`.
- The "New chat" button next to the dropdown (FE-4), the icons (FE-8). Until FE-8, the globe and arrow are simple placeholder icons.

## Interface

### `content/`

- `de.ts` must have every key that `en.ts` has. TypeScript reports a missing key.
- Each file also has `code` (`"en"`, `"de"`), `name` (`"English"`, `"Deutsch"`), `short` (`"EN"`, `"DE"`) and `languageLabel` (the dropdown's name for screen readers).
- `index.ts` exports `languages`: the list of language files, in dropdown order.

Adding a language: add a file in `content/`, add it to `languages`, and add its code to `Language` in `types.ts`. The backend must support the language too.

### `hooks/useChat.ts`

```ts
useChat(lang: Language): { messages: Message[]; status: ConversationStatus; send(text: string): void }
```

- `send` sends `lang` with the question. Everything else is as in FE-1.

### Components

- Every component that shows text gets a `content` prop with the current language file, instead of importing `en`.
- New `LanguageSelect({ content, onChange })`: the dropdown. It reads the options from `languages`, so a new language shows without changing its code.

## Behaviour

- The app starts in English.
- The dropdown button shows the globe, the `short` of the current language and an arrow. Clicking it opens the list; clicking it again closes it. The button tells screen readers whether the list is open.
- The list shows every language by its `name`. The current one has a check mark.
- Choosing a language closes the list, changes all interface text and sets the page's `lang` attribute, so screen readers pronounce the text correctly. The next question is sent with the new language.
- Escape closes the list without changing the language.
- Switching the language in the middle of a conversation keeps the conversation and its session. Old messages stay as they are; new answers come in the new language. This is the design decision.

## Preconditions / Postconditions

**Preconditions:** FE-9 is done and its tests pass.

**Postconditions:** All earlier tests and the new tests pass. `npm run lint` and `npm run build` pass.

## Edge cases

| Problem | What happens |
|---|---|
| The user switches the language while an answer is loading | The answer arrives in the language it was asked in. The next question uses the new language. |
| The hint examples ("Abschnitt 7") in German | Tried in the browser. If the backend does not understand them, the examples stay in English. |

## Acceptance criteria (Given-When-Then)

**Normal path**

- **Given** the app is open in English
- **When** I choose Deutsch in the dropdown and ask a question
- **Then** the header, welcome message, input placeholder, hint and disclaimer are in German, and the question is sent with `lang: "de"`

**Something goes wrong**

- **Given** I have chosen Deutsch
- **When** the request fails
- **Then** the error message is in German

## Design

The Figma design, screens "Welcome Screen _German" and "Deutsch Selected":

| Part | What to measure |
|---|---|
| Dropdown button | Globe size, font of "EN"/"DE", arrow, spacing |
| Open list | Width, padding, radius, shadow, font, check mark, colour of the hovered option |
