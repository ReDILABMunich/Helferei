# 003: Interface text comes through a `content` prop

## Context

Until FE-2, every component imported `content/en.ts` itself, so the interface could only be English. With the language dropdown (FE-2), every piece of interface text must change when the user chooses another language. Later, someone may add a third language.

There were two ways to give components the current language's text:

- **Props:** `App` keeps the chosen language and passes its text to each component as a prop.
- **React Context:** components read the text with a hook, without props.

## Decision

`App` keeps the chosen language in state. It finds that language's file in `content/index.ts` and passes it to each component as a `content` prop. Components do not import language files, only their type.

`LanguageSelect` reads the list of languages from `content/index.ts`, so a new language appears in the dropdown without changing its code.

## Consequences

- One place knows the language: `App`. The flow is easy to follow, from the dropdown up to `App` and down to each component.
- Components can be tested in any language by passing `content={de}`.
- No new layer rule is needed. Components already may import `content`.
- `App.tsx` passes `content` to every component, and `MessageList` passes the welcome text on to `BotMessage`.
- Adding a language means: a file in `content/`, a line in `languages`, and its code in `Language` in `types.ts`. The backend must support it too.

## When to reconsider

- If `content` has to be passed through many levels of components. Then React Context is the better choice.
- If the app needs plurals, dates or numbers formatted per language. Then an i18n library is worth its cost.
