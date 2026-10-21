import { useState } from "react";
import type { KeyboardEvent } from "react";
import type { en } from "../content/en";

const MAX_LENGTH = 800;

type MessageInputProps = {
  content: typeof en;
  onSend: (text: string) => void;
  sending: boolean;
};

function MessageInput({ content, onSend, sending }: MessageInputProps) {
  const [text, setText] = useState("");
  const tooLong = text.length > MAX_LENGTH;

  function submit() {
    if (sending || tooLong || text.trim() === "") return;
    onSend(text);
    setText("");
  }

  function handleKeyDown(event: KeyboardEvent<HTMLTextAreaElement>) {
    if (event.key !== "Enter" || event.shiftKey) return;
    event.preventDefault();
    submit();
  }

  return (
    <div className={`flex items-end pt-2 pr-3 pb-3 pl-2 bg-white border-3 rounded-8 ${tooLong ? "border-red-500" : "border-brand-500"}`}>
      <div className="flex-1 flex flex-col pt-3 px-3">
        <textarea
          className="h-9.5 resize-none outline-none text-body placeholder:text-neutral-300"
          value={text}
          onChange={(event) => setText(event.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={content.inputPlaceholder}
          aria-invalid={tooLong}
        />
        <div className={`flex justify-between items-end ${tooLong ? "mt-3 pt-3 border-t border-neutral-700" : "h-6"}`}>
          {tooLong && (
            <p className="flex gap-2 pl-3 text-body text-red-600">
              {/* Placeholder until the icon library (FE-8). */}
              <svg viewBox="0 0 40 34" aria-hidden="true" className="w-7 shrink-0">
                <path d="M20 2 L38 32 H2 Z" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinejoin="round" />
                <path d="M20 12 V22" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" />
                <circle cx="20" cy="27" r="1.5" fill="currentColor" />
              </svg>
              {content.tooLong}
            </p>
          )}
          <span className={`ml-auto text-caption ${tooLong ? "text-red-600" : text ? "text-neutral-800" : "text-neutral-300"}`}>
            {`${text.length || ""}/${MAX_LENGTH}`}
          </span>
        </div>
      </div>
      <button
        type="button"
        aria-label={content.send}
        onClick={submit}
        disabled={tooLong}
        className="flex justify-center items-center w-14 h-12 px-4 py-3 bg-brand-500 rounded-8 disabled:bg-neutral-100 disabled:text-neutral-300"
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
