import { useCallback, useRef, useState } from "react";
import { sendChat } from "../api/chat";
import type { ConversationStatus, Message } from "../types";

export function useChat() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [status, setStatus] = useState<ConversationStatus>("idle");

  // useRef, not useState: it updates at once, so a fast second send is blocked.
  const isSending = useRef(false);
  const sessionId = useRef<string | null>(null);
  const nextId = useRef(0);

  const send = useCallback((text: string): void => {
    if (isSending.current || text.trim() === "") return;

    isSending.current = true;
    setStatus("sending");
    setMessages((previous) => [
      ...previous,
      { id: nextId.current++, role: "user", text, breadcrumb: null },
    ]);

    sendChat({ message: text, session_id: sessionId.current, lang: "en" })
      .then((reply) => {
        sessionId.current = reply.session_id;
        setMessages((previous) => [
          ...previous,
          {
            id: nextId.current++,
            role: "bot",
            text: reply.answer,
            breadcrumb: reply.breadcrumb || null,
          },
        ]);
        setStatus("idle");
      })
      .catch(() => {
        setStatus("failed");
      })
      .finally(() => {
        isSending.current = false;
      });
  }, []);

  return { messages, status, send };
}
