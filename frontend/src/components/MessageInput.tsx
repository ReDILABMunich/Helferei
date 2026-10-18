import { useState } from "react";
import type { KeyboardEvent } from "react";
import { en } from "../content/en";

type MessageInputProps = {
  onSend: (text: string) => void;
  sending: boolean;
};

function MessageInput({ onSend, sending }: MessageInputProps) {
  const [text, setText] = useState("");

  function submit() {
    if (sending || text.trim() === "") return;
    onSend(text);
    setText("");
  }

  function handleKeyDown(event: KeyboardEvent<HTMLTextAreaElement>) {
    if (event.key !== "Enter" || event.shiftKey) return;
    event.preventDefault();
    submit();
  }

  return (
    <div className="flex items-end pt-2 pr-3 pb-3 pl-2 bg-white border-3 border-brand-500 rounded-8">
      <textarea
        className="flex-1 h-15.5 pt-3 px-3 resize-none outline-none text-body placeholder:text-neutral-300"
        value={text}
        onChange={(event) => setText(event.target.value)}
        onKeyDown={handleKeyDown}
        placeholder={en.inputPlaceholder}
      />
      <button
        type="button"
        aria-label={en.send}
        onClick={submit}
        className="flex justify-center items-center w-14 h-12 px-4 py-3 bg-brand-500 rounded-8"
      >
        {/* Placeholder until the icon library (FE-8). */}
        <svg viewBox="0 0 24 24" aria-hidden="true" className="w-6">
          <path d="M21 3 L3 10.5 L10.5 13.5 L13.5 21 Z M10.5 13.5 L21 3" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinejoin="round" />
        </svg>
      </button>
    </div>
  );
}

export default MessageInput;
