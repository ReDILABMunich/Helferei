# Atlas Frontend Architecture

## Class diagram

The things the frontend keeps track of, their fields, and how they relate. It covers all eight Phase 4 tickets, not only the P0 ones, so the structure does not have to change when the P1 and P2 tickets are built.

```mermaid
classDiagram
    class Conversation {
        sessionId: string | null
        language: Language
        status: ConversationStatus
        messages: Message[]
        failedQuestion: string | null
    }

    class Message {
        id: string
        role: "user" | "bot"
        text: string
        breadcrumb: string | null
    }

    class Language {
        <<enumeration>>
        en
        de
    }

    class ConversationStatus {
        <<enumeration>>
        idle
        sending
        failed
    }

    class ChatRequest {
        message: string
        session_id: string | null
        lang: Language
    }

    class ChatReply {
        answer: string
        session_id: string
        breadcrumb: string
    }

    class InterfaceText {
        welcome: string
        placeholder: string
        hint: string
        disclaimer: string
        errorMessage: string
    }

    Conversation "1" *-- "0..*" Message : holds
    Conversation --> Language : speaks
    Conversation --> ConversationStatus : is in
    Conversation ..> ChatRequest : sends
    Conversation ..> ChatReply : receives
    InterfaceText "1" --> "1" Language : one per
```

- **Conversation**: one chat session. `sessionId` is `null` until the first answer arrives. `failedQuestion` keeps the question that failed, so it can be retried.
- **Message**: one bubble. `breadcrumb` is only set on bot messages.
- **ChatRequest / ChatReply**: the shape of `POST /chat` on the backend. Field names follow the backend (`session_id`, `lang`).
- **InterfaceText**: every piece of text the interface shows, including the welcome message. One set per language. See [decision 001](../decisions/001-welcome-message-is-interface-text.md).
