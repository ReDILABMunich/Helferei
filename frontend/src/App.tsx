import { useState } from "react";
import ChatHeader from "./components/ChatHeader";
import MessageList from "./components/MessageList";
import MessageInput from "./components/MessageInput";
import ErrorCard from "./components/ErrorCard";
import { sendChat } from "./lib/api";
import type { Message } from "./types";
import "./App.css";

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

  return (
    <main className="app">
      <ChatHeader />
      <MessageList messages={messages} />
      {loading && <p>...</p>}
      {error && <ErrorCard text={error} onRetry={() => send(lastMessage)} />}
      <MessageInput
        value={input}
        onChange={setInput}
        onSend={handleSend}
        disabled={loading}
      />
    </main>
  );
}

export default App;
