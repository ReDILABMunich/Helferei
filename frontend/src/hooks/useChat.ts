import { useCallback, useRef, useState } from "react";
import { sendChat } from "../api/chat";
import type { ConversationStatus, Language, Message } from "../types";

export function useChat(lang: Language) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [status, setStatus] = useState<ConversationStatus>("idle");

  // useRef, not useState: it updates at once, so a fast second send is blocked.
  const isSending = useRef(false);
  const sessionId = useRef<string | null>(null);
  const nextId = useRef(0);
  const lastQuestion = useRef("");

  // Sends a question that is already in the message list.
  const request = useCallback((text: string): void => {
    isSending.current = true;
    setStatus("sending");

    sendChat({ message: text, session_id: sessionId.current, lang })
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
  }, [lang]);

  const send = useCallback((text: string): void => {
    if (isSending.current || text.trim() === "") return;

    lastQuestion.current = text;
    setMessages((previous) => [
      ...previous,
      { id: nextId.current++, role: "user", text, breadcrumb: null },
    ]);
    request(text);
  }, [request]);

  const retry = useCallback((): void => {
    if (isSending.current) return;
    request(lastQuestion.current);
  }, [request]);

  const reset = useCallback((): void => {
    setMessages([]);
    sessionId.current = null;
  }, []);

  return { messages, status, send, retry, reset };
}
