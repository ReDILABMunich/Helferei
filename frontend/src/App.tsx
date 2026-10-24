import { useEffect, useState } from "react";
import AppHeader from "./components/AppHeader";
import Disclaimer from "./components/Disclaimer";
import ErrorMessage from "./components/ErrorMessage";
import HintStrip from "./components/HintStrip";
import MessageInput from "./components/MessageInput";
import MessageList from "./components/MessageList";
import NewChatDialog from "./components/NewChatDialog";
import ThinkingIndicator from "./components/ThinkingIndicator";
import { languages } from "./content";
import { en } from "./content/en";
import { useChat } from "./hooks/useChat";
import type { Language } from "./types";

function App() {
  const [lang, setLang] = useState<Language>("en");
  const content = languages.find((language) => language.code === lang) ?? en;
  const { messages, status, send, retry, reset } = useChat(lang);
  const [isNewChatDialogOpen, setIsNewChatDialogOpen] = useState(false);

  function startNewChat() {
    setIsNewChatDialogOpen(false);
    reset();
  }

  useEffect(() => {
    document.documentElement.lang = lang;
  }, [lang]);

  return (
    <div className="h-full flex flex-col gap-3">
      <AppHeader content={content} onLanguageChange={setLang} onNewChat={() => setIsNewChatDialogOpen(true)} />
      <main className="flex-1 min-h-0 overflow-y-auto">
        <div className="mx-auto max-w-content flex flex-col gap-3">
          <MessageList content={content} messages={messages} />
          {status === "sending" && <ThinkingIndicator content={content} />}
          {status === "failed" && <ErrorMessage content={content} onRetry={retry} />}
        </div>
      </main>
      <footer className="w-full mx-auto max-w-content flex flex-col gap-1 py-5">
        <HintStrip content={content} />
        <div className="flex flex-col gap-3">
          <MessageInput content={content} onSend={send} sending={status === "sending"} />
          <Disclaimer content={content} />
        </div>
      </footer>
      {isNewChatDialogOpen && (
        <NewChatDialog content={content} onConfirm={startNewChat} onCancel={() => setIsNewChatDialogOpen(false)} />
      )}
    </div>
  );
}

export default App;
