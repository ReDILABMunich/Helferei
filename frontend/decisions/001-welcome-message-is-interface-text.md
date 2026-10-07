# 001: The welcome message is interface text, not a message

## Context

The chat always starts with a welcome message from Atlas. In the prototype built for the mid-term review, the welcome message is the first item in the conversation's `messages` list, so it is stored like an answer from the agent.

Two tickets do not work well with that:

- Ticket 2 (Switch the chat to German): when the user switches language, the welcome message must switch too. An item in the message list stays in the language it was created in.
- Ticket 4 (Start a new conversation): after a reset, only the welcome message should be left. With the welcome in the list, the reset has to remove everything except the first item.

## Decision

The welcome message lives in `InterfaceText`, one version per language, next to the other interface text. The conversation's `messages` list holds only real questions and answers. The interface always shows the welcome message above the list.

## Consequences

- Switching language changes the welcome message with the rest of the interface.
- A reset empties the list; the welcome message stays without extra code.
- An empty `messages` list means "no question asked yet".

## When to reconsider

- If the welcome message has to come from the backend (for example, if it changes per user or per session).
- If the design changes so that the welcome message scrolls away with the conversation and is not always shown.
