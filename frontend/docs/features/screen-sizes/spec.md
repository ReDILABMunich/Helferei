# FE-7: Match the layout to the other screen sizes

## What it does

The Figma design has five screen sizes: mobile, tablet, small desktop, default desktop and very wide desktop. FE-9 matched the default desktop. This ticket makes the layout match the Figma design on the other four sizes. The smallest size is 390px wide.

## What it does not touch

- The chat behaviour. No change to `useChat`, `api/` or what the components do.
- The default desktop size (FE-9). It must look the same as before.
- The icons from the icon library (FE-8).
- The breadcrumb line (FE-5).
- A native mobile app, and widths below 390px.

## Interface

- `src/index.css`: the Figma frame widths become the Tailwind breakpoints, in the `@theme` block, next to the other tokens.
- Components get responsive Tailwind classes (for example `md:px-8`). Their props do not change.
- No new components.

## Behaviour

- Each screen size uses the layout of its Figma frame, from the breakpoint of that frame up to the next one.
- Breakpoints, sizes and spacing come only from the tokens. Raw pixel values appear only in `src/index.css`.
- The page never scrolls sideways, from 390px up.
- The header and the input stay in place; only the message list scrolls. (Already true from FE-9; it must stay true on every size.)
- A long German word or a URL wraps inside the bubble. (Already true from FE-9 for both bubbles; it must stay true on every size.)

## Preconditions / Postconditions

**Preconditions:** FE-9 is done. All tests pass.

**Postconditions:** All existing tests pass. `npm run lint` and `npm run build` pass. The default desktop looks the same as before.

## Edge cases

| Problem | What happens |
|---|---|
| A width between two Figma frames | The layout of the smaller frame is used, stretched to fit. |
| The header on mobile: logo, title, subtitle, language dropdown and "New chat" button | Arranged as in the mobile frame; nothing is cut off or pushes the page wider. |
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

These checks are done by eye in the browser, side by side with the Figma file, at each frame width. Layout cannot be measured in the test environment (jsdom), so there are no new automated tests; the existing tests make sure the behaviour did not change. The horizontal scroll check is also done in the browser: at 390px, `document.documentElement.scrollWidth` equals the window width.

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
