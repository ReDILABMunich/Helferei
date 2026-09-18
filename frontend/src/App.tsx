import { useState } from "react";
import ReactMarkdown from "react-markdown";
import { sendChat } from "./lib/api";
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
      <h1>Helferei Chat</h1>
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
