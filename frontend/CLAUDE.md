# Atlas Frontend

React 19 + TypeScript + Vite. The chat interface for the agent that explains the German tax registration form. Problem and MVP: [README.md](README.md).

## Commands

- `npm run dev`: start the app locally
- `npm test`: run the tests (Vitest, React Testing Library, jsdom)
- `npm run lint`: oxlint and the layer check (dependency-cruiser)
- `npm run build`: type check and production build

Run `npm test`, `npm run lint` and `npm run build` before proposing any change as done. All three must pass.

## Architecture

Read [docs/architecture.md](docs/architecture.md) before adding or moving a file. It has the class diagram and the package diagram.

Layers in `src/`, imports only go downwards:

| Layer | Folder | May import |
|---|---|---|
| app | `main.tsx`, `App.tsx` | components, hooks, content, types |
| components | `components/` | content, types |
| hooks | `hooks/` | api, types |
| api | `api/` | types |
| content | `content/` | types |
| types | `types.ts` | nothing |

- Only `hooks` calls the backend. Components get data and callbacks through props. See [decision 002](decisions/002-only-hooks-talk-to-the-backend.md).
- The welcome message lives in `content/`, not in the message list. See [decision 001](decisions/001-welcome-message-is-interface-text.md).
- `npm run lint` enforces the layer rules. Never edit `.dependency-cruiser-known-violations.json` to make a new violation pass; fix the import instead.

## How we work

Each ticket goes through Read, Plan, Implement, Verify, on its own branch, and ends in a pull request.

1. **Spec first.** Write `docs/features/<name>/spec.md` with these sections, in this order. Each rule is written in one section only; other sections refer to it instead of repeating it.
   - `# FE-N: <ticket title>`
   - `## What it does`: a short summary.
   - `## What it does not touch`: what is left for other tickets, with their IDs.
   - `## Interface`: what goes in and what comes out of each new function or hook.
   - `## Behaviour (state machine)`: if the feature has states, a table with From, Event, To and What happens. Otherwise the rules as a list.
   - `## Preconditions / Postconditions`: what must be true before, and what is guaranteed after.
   - `## Edge cases`: what can go wrong that Behaviour does not already cover, and what happens then.
   - `## Acceptance criteria (Given-When-Then)`: two checks, one for the normal path and one for something going wrong.
   - `## Design`: what has to match the Figma design.
2. **Approval.** Wait for approval of the two Given-When-Then checks before writing tests. Each check becomes a test that goes through the screen; every other rule in the spec gets its own smaller test.
3. **Test first.** Write the test, show that it fails, then write the smallest code that makes it pass.
4. **Spec before code.** If the code needs to do something the spec does not say, update the spec first.
5. **Decisions.** Record important decisions in `decisions/NNN-name.md`: context, decision, consequences, when to reconsider.
6. **Commits.** One decision per commit. The spec, tests and code for that decision go together, and every commit keeps the tests green. Do not commit without approval: list the changed files first and ask.

## Rules

- Ask before adding a new dependency.
- If you see a problem outside the current ticket or spec, report it. Do not fix it in the same change.
- No user-visible text in `.tsx` files. All interface text comes from `content/`.
- No team members' names in any file that is pushed. Refer to roles or artefacts, for example "the Figma design" or "the backend".
