# FE-8: Use the icons from Helferei's icon library

## What it does

At the mid-term review the client asked that the icons come from the icon library shared in the Figma file. Until now the app used placeholder icons drawn by hand. This ticket replaces every placeholder with the matching icon from the library, and makes sure every button that only shows an icon has a label that a screen reader reads out.

## What it does not touch

- The layout and the colours. Every icon keeps the width and the colour it has today.
- The logo. It is a brand image, not an icon.
- The library icons the app does not use: `arrow-right` and `Icon Sample`.
- The send button states from the Figma "Button" component (hover, pressing, disabled). They are still open and belong to their own change.

## Interface

New file `src/components/icons.tsx`. It holds one small component per library icon, with the path data copied from the Figma file:

| Component | Library icon | viewBox |
|---|---|---|
| `ArrowDownIcon` | `arrow-single-down` | `0 0 12 7.9` |
| `ArrowUpIcon` | `arrow-single-up` | `0 0 12 7.67` |
| `CautionIcon` | `caution` | `0 0 40 33.9474` |
| `CloseIcon` | the X icon (named `Vector` in the Figma file) | `0 0 20 19.69` |
| `DocAddIcon` | `doc-add` | `0 0 28 33.5182` |
| `GlobeIcon` | `globe` | `0 0 24 22.1838` |
| `InfoIcon` | `Info` | `0 0 40 38.97` |
| `MenuIcon` | `menu` | `0 0 48 34.3448` |
| `NavigationIcon` | `navigation` | `0 0 24 24.4832` |
| `RefreshIcon` | the refresh icon (named `50` in the Figma file) | `0 0 24 25.79` |
| `TickIcon` | `tick` | `0 0 29.8 20.79` |

- In: `className` (optional), used for the width and the colour.
- Out: an `<svg>` with `aria-hidden="true"`, `fill="currentColor"` and `data-icon="<library name>"`, for example `data-icon="close"`.

The `caution` icon has two sizes in the library (28 and 40) with the same shape, so there is one component and the width comes from `className`.

The SVGs are written as React components by hand instead of loading `.svg` files with a build plugin. See [decision 004](../../../decisions/004-icons-are-inline-components.md).

## Behaviour

Where each library icon goes:

| Place | Icon | Width |
|---|---|---|
| Header, "New chat" button | `doc-add` | 28px |
| Mobile menu button | `menu` | 48px |
| Mobile menu, close button | `close` | 24px |
| Mobile menu, tick next to the current language | `tick` | 30px |
| Language dropdown button | `globe` | 24px |
| Language dropdown button, arrow | `arrow-single-down` | 12px |
| Language dropdown, tick next to the current language | `tick` | 24px |
| Hint strip button, hint open | `arrow-single-down` | 12px |
| Hint strip button, hint closed | `arrow-single-up` | 12px |
| Input, message over the limit | `caution` | 28px |
| Send button | `navigation` | 24px |
| Error message | `caution` | 40px |
| Error message, "Try again" button | `refresh` | 24px |
| New chat dialog, close button | `close` | 20px |
| New chat dialog, next to the title | `info` | 40px |

- The height of each icon follows from its width and its viewBox.
- Each icon takes the colour of the text around it (`currentColor`), so the colours do not change.
- Every icon is hidden from screen readers (`aria-hidden`). An icon never carries meaning alone: the text next to it or the label of its button does.
- Every button that shows only an icon has a label from `content/`, in the current language:

| Button | Label (English) |
|---|---|
| Header, "New chat" | `newChat.button` |
| Mobile menu button | `menu.open` |
| Mobile menu, close | `menu.close` |
| Hint strip button | `toggleHint` |
| Send | `send` |
| New chat dialog, close | `newChat.close` |

## Preconditions / Postconditions

**Preconditions:** FE-7 is done. All tests pass.

**Postconditions:** No placeholder icon is left in `src/`. All existing tests pass. `npm run lint` and `npm run build` pass. The layout and the colours look the same as before; only the shape of the icons changes.

## Edge cases

| Problem | What happens |
|---|---|
| A library icon is not square | Only the width is set; the height follows from the viewBox, so the icon is not stretched. |
| A place is smaller in the app than the icon in the library (the mobile menu tick, the dropdown tick) | The icon is scaled down to the width the place has today. |
| The language changes | The button labels change with it, because they come from `content/`. |
| The send button is disabled | The icon turns grey with the button, because it uses `currentColor`. |

## Acceptance criteria (Given-When-Then)

**Normal path**

- **Given** the app is open
- **When** I look at the header, the hint strip, the input, an error message and the new chat dialog
- **Then** each icon is the library icon listed in Behaviour (checked through `data-icon`)

**Something goes wrong**

- **Given** a screen reader user has switched the app to German
- **When** they move to a button that shows only an icon
- **Then** the screen reader reads out its German label

Every other rule in Behaviour (the mobile menu icons, the language dropdown icons, the hint strip arrow changing) gets its own smaller test. That the icons look right is checked by eye in the browser, side by side with the Figma file.

## Design

From the "Icons" frame in the Figma file:

- The path data of each icon, copied as SVG from the Figma file.
- Black (`#000000`) in the Figma file becomes `currentColor`.
- Sizes: the widths in the Behaviour table. They are the widths the app already uses, which match the Figma frames.
