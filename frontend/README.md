# Atlas Frontend

Atlas is the web version of the agent that explains the German tax registration form (Fragebogen zur steuerlichen Erfassung für Einzelunternehmen).

## Problem

People who are starting to work as self-employed in Germany struggle to understand the tax registration form. The form is in German and uses technical tax language.

## MVP

Anyone who opens the Atlas web app can find out what a field of the tax registration form means by chatting with the existing agent in English or German.

## How to run

You need Node.js (version 22 works).

```bash
cd frontend
npm install
npm run dev
```

The app opens at http://localhost:5173 and talks to the live backend on Render.

| Command | What it does |
|---|---|
| `npm run dev` | Starts the app locally |
| `npm test` | Runs the tests |
| `npm run lint` | Checks the code and the layer rules |
| `npm run build` | Checks the types and builds the site for production |

Every push to `main` is deployed to Vercel automatically. Every other branch gets its own preview link, posted as a comment on its pull request.

## Docs

- [Architecture](docs/architecture.md): class diagram, package diagram and layer rules
- [Decisions](decisions/): why things are the way they are
- [Feature specs](docs/features/): one spec per ticket (FE-1 to FE-8)
- [CLAUDE.md](CLAUDE.md): how we work on this code
