# FE-11: See the hover and pressed states of the buttons

## What it does

Makes the buttons follow the Figma "Button" component:

- The send button turns `brand-400` on hover.
- The retry button has a `red-200` border.
- The "New chat" dialog buttons are as wide as their text ("Hug"), so the German text does not wrap.
- Every enabled button shows the pointer cursor on hover.

## What it does not touch

Behaviour, focus styles, the "Link" button type, text colours, the icons (FE-8).

## Interface

No new functions or props.

## Behaviour (state machine)

No new states. The other button states are already in the code and stay as they are.

## Preconditions / Postconditions

- Before: FE-8 is done.
- After: all earlier tests, `npm run lint` and `npm run build` pass.

## Edge cases

- The disabled send button stays grey and keeps the arrow cursor on hover.
- If a button text is too long for the dialog, it wraps instead of overflowing.

## Acceptance criteria (Given-When-Then)

**Normal path**

- **Given** the app is open on desktop
- **When** I move the mouse over the send button
- **Then** it turns `brand-400` and the cursor is a pointer

**Something goes wrong**

- **Given** German is selected and the app is 390px wide
- **When** I open the "New chat" dialog
- **Then** both buttons stay on one line

Checked by eye in the browser. Hover colours and text width cannot be measured in jsdom, so there are no new tests.

## Design

The Figma "Button" component: default, hover and pressed colours, and "Hug" sizes.
