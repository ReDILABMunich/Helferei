# FE-9: Match the chat screen to the Figma design

## What it does

The chat screen from FE-1 gets the look of the Figma design on the default desktop size: colours, fonts, spacing, sizes, corner radii and shadows. Three parts of the design that FE-1 does not have yet are added: the header (logo, title, subtitle), the hint strip above the input, which can be collapsed, and the disclaimer below it. The rest of the behaviour does not change.

## What it does not touch

- The chat behaviour. No change to `useChat`, `api/` or what the FE-1 components do.
- Other screen sizes: mobile, tablet, small desktop, very wide desktop (FE-7).
- The language dropdown in the header (FE-2).
- The icons from the icon library (FE-8). Until then, simple placeholder icons are used where the design shows one.
- The retry button (FE-3), the "New chat" button (FE-4), the breadcrumb line (FE-5), the character counter (FE-6).

## Interface

- `src/index.css`: Tailwind and the design tokens in one `@theme` block: colour scales, font families, type scale, radii, shadows.
- Components get Tailwind classes. Their props do not change.
- New components without props: `AppHeader`, `HintStrip`, `Disclaimer`. Their text comes from `content/en.ts`. `HintStrip` keeps its own open or closed state.

## Behaviour

- Colours, font sizes, radii and shadows come only from the tokens. Raw values (hex colours, pixel sizes) appear only in `src/index.css`.
- Class names are written in full, for example `bg-brand-500`. Tailwind does not see class names built from pieces.
- The header and the input stay in place; only the message list scrolls.
- The hint strip is open when the app starts. Its toggle button hides the hint text; clicking it again shows the text. The button tells screen readers whether the hint is open.

## Preconditions / Postconditions

**Preconditions:** FE-1 is done and its tests pass.

**Postconditions:** All FE-1 tests and the hint strip tests pass. `npm run lint` and `npm run build` pass.

## Edge cases

| Problem | What happens |
|---|---|
| A very long word or URL in an answer | Wraps inside the bubble where it reaches the edge, no horizontal scroll. |
| A long conversation | The message list scrolls; the header and the input do not move. |

## Acceptance criteria (Given-When-Then)

**Normal path**

- **Given** the app is open in a browser at the default desktop width
- **When** I ask a question and get an answer
- **Then** the header, the welcome message, my question, the loading indicator, the answer, the hint strip, the input and the disclaimer match the Figma design

**Something goes wrong**

- **Given** the app is open at the default desktop width
- **When** the request fails
- **Then** the error message matches the Figma design

These checks are done by eye in the browser, side by side with the Figma file. The FE-1 tests make sure the chat behaviour did not change; the hint strip has its own tests.

## Design

Measured in the Figma file, default desktop size:

| Part | What to measure |
|---|---|
| Page | Width of the content column, page background |
| Header | Height, logo size, title and subtitle fonts |
| Bot bubble | Padding, radius, shadow, avatar size |
| User bubble | Padding, radius, colour |
| Message list | Space between messages |
| Loading indicator | Font, dots |
| Error message | Colours, padding, radius |
| Hint strip | Colours, padding, radius |
| Input | Height, padding, border, send button size |
| Disclaimer | Font size, colour |
