# 004: Icons are inline React components

## Context

FE-8 replaces the placeholder icons with the icons from the icon library in the Figma file. The library has eleven icons the app uses. The same icon has a different colour in different places (red in the error message, orange in the new chat dialog, grey on the disabled send button) and changes colour on hover.

An SVG loaded as an image (`<img src="tick.svg">`) cannot see the page's CSS, so it keeps the colour written in the file. To take the colour from CSS (`currentColor`), the SVG has to be inside the page's HTML. There were two ways to do that:

- **By hand:** copy the path data from the Figma file into small React components in one file.
- **With a build plugin:** keep the exported `.svg` files in the repo and let `vite-plugin-svgr` turn them into components.

## Decision

The icons are React components in `src/components/icons.tsx`, with the path data copied from the Figma file. One shared `Icon` component writes the `<svg>` with `aria-hidden="true"`, `fill="currentColor"` and `data-icon="<library name>"`. Each icon gives only its name, its viewBox and its paths. A component sets the width and the colour through `className`.

## Consequences

- No new dependency and no build or TypeScript configuration.
- Every icon takes the colour of the text around it, so hover, disabled and coloured states work without extra code.
- The rules for every icon (hidden from screen readers, colour from CSS) are written once, in `Icon`.
- Tests find an icon by its library name through `data-icon`.
- The path data is long and not readable by hand. When the designer changes an icon, its path data has to be copied again from the Figma file.

## When to reconsider

- If the library grows to many more icons, or the designer changes icons often. Then keeping the `.svg` files in the repo and using `vite-plugin-svgr` (with SVGO) is less work.
