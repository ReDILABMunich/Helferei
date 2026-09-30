import { useState } from "react";
import AppHeader from "./components/AppHeader";
import MessageList from "./components/MessageList";
import MessageInput from "./components/MessageInput";
import ErrorCard from "./components/ErrorCard";
import { sendChat } from "./lib/api";
import { en } from "./content/en";
import type { Message } from "./types";

function App() {
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [lastMessage, setLastMessage] = useState("");
  const [responseId, setResponseId] = useState<string | null>(null);

  async function send(text: string) {
    setError(null);
    setLoading(true);

    try {
      const reply = await sendChat(text, responseId);
      const botMessage: Message = { role: "bot", text: reply.answer };
      setMessages((previous) => [...previous, botMessage]);
      setResponseId(reply.responseId);
    } catch (err) {
      console.log(err);
      setError("Something went wrong. Please try again.");
    } finally {
      setLoading(false);
    }
  }

  async function handleSend() {
    if (input.trim() === "") return;

    const text = input;
    const userMessage: Message = { role: "user", text };
    setMessages((previous) => [...previous, userMessage]);
    setInput("");
    setLastMessage(text);

    await send(text);
  }

  // Üç bant: header ve footer sabit, sadece ortadaki bant kayar.
  return (
    <div className="flex h-dvh flex-col bg-neutral-50">
      <AppHeader onNewChat={() => {}} />

      <main className="flex-1 overflow-y-auto">
        <div className="mx-auto max-w-[1012px] space-y-6 px-5 py-6 lg:px-8">
          <MessageList messages={messages} />
          {loading && <p>...</p>}
          {error && <ErrorCard text={error} onRetry={() => send(lastMessage)} />}
        </div>
      </main>

      <footer className="bg-neutral-50 pb-3">
        <div className="mx-auto max-w-[1012px] px-5 lg:px-8">
          <MessageInput
            value={input}
            onChange={setInput}
            onSend={handleSend}
            disabled={loading}
          />
          <p className="mt-2 text-center text-caption text-neutral-500">{en.disclaimer}</p>
        </div>
      </footer>
    </div>
  );
}

export default App;
