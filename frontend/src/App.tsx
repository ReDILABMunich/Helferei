import { useState } from "react";
import ReactMarkdown from "react-markdown";
import { ping, sendChat } from "./lib/api";
import "./App.css";

type Message = {
  role: "user" | "bot";
  text: string;
};

function App() {
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [lastMessage, setLastMessage] = useState("");
  const [backendMessage, setBackendMessage] = useState<string | null>(null);
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

  async function handlePing() {
    setLoading(true);

    try {
      const message = await ping();
      setBackendMessage(message);
    } catch (err) {
      console.log(err);
      setBackendMessage("Could not reach the backend.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="app">
      <h1>Helferei Chat</h1>
      <button
        onClick={handlePing}
        disabled={loading}>
        Check backend
      </button>
      {backendMessage && <p>{backendMessage}</p>}
      <div>
        {messages.map((message, index) => (
          <div key={index} className="message">
            <strong>{message.role}:</strong>
            {message.role === "bot" ? (
              <ReactMarkdown>{message.text}</ReactMarkdown>
            ) : (
              <span> {message.text}</span>
            )}
          </div>
        ))}
      </div>
      {loading && <p>...</p>}
      {error && (
        <p>
          {error} <button onClick={() => send(lastMessage)}>Try again</button>
        </p>
      )}
      <input
        placeholder="Type a message"
        value={input}
        onChange={(e) => setInput(e.target.value)}
      />
      <button
        onClick={handleSend}
        disabled={loading}>
        Send
      </button>
    </main>
  );
}

export default App;
