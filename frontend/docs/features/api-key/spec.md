# FE-16: Send the API key with every chat request

## What it does

The backend now rejects every chat request without a valid API key. The frontend sends the key in a header, so the chat works again.

## What it does not touch

- The backend, including the key check and the rate limit.
- The error message and the "Try again" button (FE-3). A rejected request uses them as they are.
- The body of the request.

The key is not a secret: it is built into the JavaScript and anyone can read it in the browser. This ticket does not try to hide it.

## Interface

### `api/chat.ts`

`sendChat` keeps its input and its output. Every request gets one more header:

| Header | Value |
|---|---|
| `X-API-Key` | `import.meta.env.VITE_API_KEY` |

### Environment variable

`VITE_API_KEY` holds the value of the key. It is set in two places and never in a file that is pushed:

- Locally: `frontend/.env.local`, which git ignores.
- In production: the Vercel project settings.

`frontend/.env.example` is pushed and shows the name of the variable, with an empty value.

Vite writes the value into the JavaScript at build time, so a new value needs a new build.

## Behaviour (state machine)

The request follows the states of FE-1 and FE-3. It does not add new states.

- Every request to `/chat` carries the `X-API-Key` header, including a retry.

## Preconditions / Postconditions

**Preconditions:** The backend checks the `X-API-Key` header and allows it through CORS. `VITE_API_KEY` is set in the Vercel project settings before this ticket is merged.

**Postconditions:** All earlier tests and the new tests pass. `npm run lint` and `npm run build` pass. The live chat answers a question.

## Edge cases

| Problem | What happens |
|---|---|
| `VITE_API_KEY` was not set at build time | The backend returns 401. The user sees the existing error message and "Try again". |
| The key was changed on the backend | The same as above, until a new build has the new value. |

## Acceptance criteria (Given-When-Then)

**Normal path**

- **Given** the API key is set
- **When** I send a question
- **Then** the request carries the key in the `X-API-Key` header and the answer is shown

**Something goes wrong**

- **Given** the backend rejects the key
- **When** I send a question
- **Then** the error message and "Try again" are shown

## Design

Nothing new to measure in the Figma design.
