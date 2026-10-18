import AppHeader from "./components/AppHeader";
import ErrorMessage from "./components/ErrorMessage";
import MessageInput from "./components/MessageInput";
import MessageList from "./components/MessageList";
import ThinkingIndicator from "./components/ThinkingIndicator";
import { useChat } from "./hooks/useChat";

function App() {
  const { messages, status, send } = useChat();

  return (
    <div className="h-full flex flex-col gap-3">
      <AppHeader />
      <main className="flex-1 min-h-0 overflow-y-auto">
        <div className="mx-auto max-w-content flex flex-col gap-3">
          <MessageList messages={messages} />
          {status === "sending" && <ThinkingIndicator />}
          {status === "failed" && <ErrorMessage />}
        </div>
      </main>
      <MessageInput onSend={send} sending={status === "sending"} />
    </div>
  );
}

export default App;
