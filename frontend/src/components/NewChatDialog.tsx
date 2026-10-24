import { useId } from "react";
import type { KeyboardEvent, MouseEvent } from "react";
import type { en } from "../content/en";

type NewChatDialogProps = {
  content: typeof en;
  onConfirm: () => void;
  onCancel: () => void;
};

function NewChatDialog({ content, onConfirm, onCancel }: NewChatDialogProps) {
  const titleId = useId();

  function handleKeyDown(event: KeyboardEvent<HTMLDivElement>) {
    if (event.key === "Escape") onCancel();
  }

  // Only a click on the background itself, not on the dialog inside it.
  function handleBackgroundClick(event: MouseEvent<HTMLDivElement>) {
    if (event.target === event.currentTarget) onCancel();
  }

  return (
    <div onKeyDown={handleKeyDown} onClick={handleBackgroundClick}>
      <div role="dialog" aria-modal="true" aria-labelledby={titleId}>
        <button type="button" aria-label={content.newChat.close} onClick={onCancel}>
          {/* Placeholder until the icon library (FE-8). */}
          <svg viewBox="0 0 24 24" aria-hidden="true" className="w-6" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round">
            <path d="M6 6 L18 18 M18 6 L6 18" />
          </svg>
        </button>
        <h2 id={titleId}>{content.newChat.title}</h2>
        <p>{content.newChat.body}</p>
        {/* Focus starts on the least destructive button, so Enter does not clear the chat. */}
        <button type="button" onClick={onCancel} autoFocus>
          {content.newChat.cancel}
        </button>
        <button type="button" onClick={onConfirm}>
          {content.newChat.confirm}
        </button>
      </div>
    </div>
  );
}

export default NewChatDialog;
