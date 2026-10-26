# 005: The breadcrumb is split in the frontend

## Context

FE-5 shows where an answer is in the form. The backend sends the place as one string in the `breadcrumb` field of `POST /chat`, for example "Section 1: Allgemeine Angaben → Art der Tätigkeit". The backend builds this string from a list of parts and joins them with " → ". The section number and the section name are one part ("Section 1: Allgemeine Angaben", "Abschnitt 1: …" in German).

The Figma design shows each part as its own segment, with an arrow between them, and shows the section number and the section name as two segments: "Section 1 → Allgemeine Angaben → Art der Tätigkeit". Every segment but the last is blue.

There were two ways to get the segments:

- **In the frontend:** split the string the backend already sends.
- **In the backend:** send the segments as a list, which changes the API contract.

## Decision

The frontend splits the string in `components/BotMessage.tsx`: at each "→", and the first segment once more at its first ": ". Only the first segment is split at ": ", because field names further down the path can contain a colon. The rules are in the [FE-5 spec](../docs/features/breadcrumb/spec.md).

## Consequences

- No change to the backend or to the API contract, so FE-5 did not wait for backend work.
- The frontend depends on the format of the string: the " → " separator and the ": " after the section number. If the backend changes that format, the segments come out wrong. The FE-5 tests use the backend's format, but they cannot notice a change made on the backend.
- The splitting is one small function. If the backend sends a list later, the function is removed and the screen stays the same.

## When to reconsider

- When the backend can send the breadcrumb as a list of segments. Then the frontend uses that list and the splitting function is removed.
- If clicking a segment (FE-15) takes the user to the wrong part of the form.
