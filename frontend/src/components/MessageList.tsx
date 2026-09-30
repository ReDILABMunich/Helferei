import { useEffect, useRef } from "react";
import BotMessage from "./BotMessage";
import UserMessage from "./UserMessage";
import ThinkingIndicator from "./ThinkingIndicator";
import type { Message as MessageType } from "../types";

type MessageListProps = {
  messages: MessageType[];
  loading: boolean;
};

function MessageList({ messages, loading }: MessageListProps) {
  const endRef = useRef<HTMLDivElement>(null);

  // Listenin sonundaki boş div'e kaydırmak, scrollHeight hesaplamaktan
  // hem daha basit hem daha güvenilir.
  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  return (
    <div className="space-y-6">
      {/* Liste sadece sona ekleniyor, o yüzden index key şimdilik güvenli.
          Task 3'te mesajlara kalıcı id gelecek. */}
      {messages.map((message, index) =>
        message.role === "bot" ? (
          <BotMessage key={index} text={message.text} />
        ) : (
          <UserMessage key={index} text={message.text} />
        ),
      )}
      {loading && <ThinkingIndicator />}
      <div ref={endRef} />
    </div>
  );
}

export default MessageList;
