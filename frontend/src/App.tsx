import ErrorMessage from "./components/ErrorMessage";
import MessageInput from "./components/MessageInput";
import MessageList from "./components/MessageList";
import ThinkingIndicator from "./components/ThinkingIndicator";
import { useChat } from "./hooks/useChat";

function App() {
  const { messages, status, send } = useChat();

  return (
    <main>
      <MessageList messages={messages} />
      {status === "sending" && <ThinkingIndicator />}
      {status === "failed" && <ErrorMessage />}
      <MessageInput onSend={send} sending={status === "sending"} />
    </main>
  );
}

export default App;
