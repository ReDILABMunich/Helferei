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
    <div
      onKeyDown={handleKeyDown}
      onClick={handleBackgroundClick}
      className="fixed inset-0 z-20 flex justify-center items-center bg-black/60"
    >
      <div
        role="dialog"
        aria-modal="true"
        aria-labelledby={titleId}
        className="relative flex flex-col justify-center items-center gap-12.5 w-130 max-w-full pt-15 pr-6 pb-10 pl-10 bg-white border-t-4 border-orange-400 shadow-small rounded-16"
      >
        <button
          type="button"
          aria-label={content.newChat.close}
          onClick={onCancel}
          className="absolute top-6.75 right-7 text-neutral-500"
        >
          {/* Placeholder until the icon library (FE-8). */}
          <svg viewBox="0 0 20 20" aria-hidden="true" className="w-5" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round">
            <path d="M2 2 L18 18 M18 2 L2 18" />
          </svg>
        </button>
        <div className="self-stretch flex items-start gap-3 p-1">
          <div className="flex items-center p-1">
            {/* Placeholder until the icon library (FE-8). */}
            <svg viewBox="0 0 40 40" aria-hidden="true" className="w-10 text-orange-400">
              <circle cx="20" cy="20" r="18.5" fill="none" stroke="currentColor" strokeWidth="3" />
              <circle cx="20" cy="10.5" r="2.5" fill="currentColor" />
              <path d="M20 17 V31" stroke="currentColor" strokeWidth="3.5" strokeLinecap="round" />
            </svg>
          </div>
          <div className="flex-1 flex flex-col items-start gap-2">
            <h2 id={titleId} className="font-bold text-h4 text-neutral-900">
              {content.newChat.title}
            </h2>
            <p className="font-bold text-h5 text-neutral-700">{content.newChat.body}</p>
          </div>
        </div>
        <div className="self-stretch flex justify-end items-end gap-2">
          {/* Focus starts on the least destructive button, so Enter does not clear the chat. */}
          <button
            type="button"
            onClick={onCancel}
            autoFocus
            className="flex justify-center items-center w-28 h-12.5 px-4 py-2 bg-white border border-neutral-500 shadow-x-small rounded-8 text-h5 text-black hover:border-orange-500 active:border-neutral-500"
          >
            {content.newChat.cancel}
          </button>
          <button
            type="button"
            onClick={onConfirm}
            className="flex justify-center items-center w-30 h-12.5 px-4 py-3 bg-orange-400 shadow-x-small rounded-8 font-bold text-h5 text-white hover:bg-orange-500 active:bg-orange-400"
          >
            {content.newChat.confirm}
          </button>
        </div>
      </div>
    </div>
  );
}

export default NewChatDialog;
