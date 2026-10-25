# FE-7: Match the layout to the other screen sizes

## What it does

The Figma design has five screen sizes: mobile, tablet, small desktop, default desktop and very wide desktop. FE-9 matched the default desktop. This ticket makes the layout match the Figma design on the other four sizes. The smallest size is 390px wide.

On mobile the header has no room for the language dropdown and the "New chat" button, so the Figma design puts them in a menu that opens over the whole screen.

## What it does not touch

- The chat behaviour. No change to `useChat` or `api/`.
- The default desktop size (FE-9). It must look the same as before.
- The icons from the icon library (FE-8).
- The breadcrumb line (FE-5).
- A native mobile app, and widths below 390px.

## Interface

- `src/index.css`: the Figma frame widths become the Tailwind breakpoints, in the `@theme` block, next to the other tokens.
- Components get responsive Tailwind classes (for example `md:px-8`). Their props do not change.
- New component `MobileMenu`, shown in the header on mobile only. It keeps its own open or closed state.
  - In: `content`, `onLanguageChange(code)`, `onNewChat()`. The same callbacks `AppHeader` already gets.
  - Out: nothing; it calls the callbacks.
- New interface text in `content/`: the labels of the menu button and the close button.

## Behaviour

- Each screen size uses the layout of its Figma frame, from the breakpoint of that frame up to the next one.
- Breakpoints, sizes and spacing come only from the tokens. Raw pixel values appear only in `src/index.css`.
- The page never scrolls sideways, from 390px up.
- The header and the input stay in place; only the message list scrolls. (Already true from FE-9; it must stay true on every size.)
- A long German word or a URL wraps inside the bubble. (Already true from FE-9 for both bubbles; it must stay true on every size.)

**Mobile menu**

| From | Event | To | What happens |
|---|---|---|---|
| Closed | Click the menu button | Open | The menu covers the screen: logo, title, close button, subtitle, the languages (the current one has a tick), a separator, "New chat". The menu button tells screen readers the menu is open. |
| Open | Click a language | Closed | The app switches to that language. |
| Open | Click "New chat" | Closed | The "New chat" dialog from FE-4 opens. |
| Open | Click the close button or press Escape | Closed | Nothing else changes. |

## Preconditions / Postconditions

**Preconditions:** FE-9 is done. All tests pass.

**Postconditions:** All existing tests pass. `npm run lint` and `npm run build` pass. The default desktop looks the same as before.

## Edge cases

| Problem | What happens |
|---|---|
| A width between two Figma frames | The layout of the smaller frame is used, stretched to fit. |
| The window gets wider than mobile while the menu is open | The menu is hidden and the desktop header shows the dropdown and the button. |
| The new chat dialog on mobile | Fits inside the screen width. |
| The phone keyboard opens | The input stays visible above it. |

## Acceptance criteria (Given-When-Then)

**Normal path**

- **Given** the app is open at the width of one of the four Figma frames (mobile, tablet, small desktop, very wide desktop)
- **When** I ask a question and get an answer
- **Then** the header, the messages, the hint strip, the input and the disclaimer match the Figma frame for that size

**Something goes wrong**

- **Given** the app is open at 390px width
- **When** an answer contains a very long German word and a long URL
- **Then** both wrap inside the bubble, and the page has no horizontal scroll

These checks are done by eye in the browser, side by side with the Figma file, at each frame width. Layout cannot be measured in the test environment (jsdom), so these two checks have no automated tests; the existing tests make sure the behaviour did not change. Each row of the mobile menu table gets its own test. The horizontal scroll check is also done in the browser: at 390px, `document.documentElement.scrollWidth` equals the window width.

## Design

Measured in the Figma file, for each of the four frames:

| Part | What to measure |
|---|---|
| Frame | Width (becomes the breakpoint), side padding, width of the content column |
| Header | Height, logo size, title and subtitle fonts, where the language dropdown and the "New chat" button go |
| Bot bubble | Padding, avatar size, maximum width |
| User bubble | Padding, minimum and maximum width |
| Message list | Space between messages |
| Hint strip | Padding, font size |
| Input | Height, padding, send button size |
| Disclaimer | Font size |
| New chat dialog | Width, padding |
| Mobile menu (only in the mobile frame "Menu Open") | Padding, space between items, fonts, separator lines, tick size |

In the mobile frame the hint strip is wider than the screen. It is made to fit the screen width, because the page must not scroll sideways.
