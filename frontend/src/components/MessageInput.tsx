import { useEffect, useRef } from "react";
import type { KeyboardEvent } from "react";
import { AlertTriangleIcon, SendIcon } from "./icons";
import { CHAR_LIMIT, en } from "../content/en";

type MessageInputProps = {
  value: string;
  onChange: (value: string) => void;
  onSend: () => void;
  disabled: boolean;
};

const MAX_TEXTAREA_HEIGHT = 200;

function MessageInput({ value, onChange, onSend, disabled }: MessageInputProps) {
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const overLimit = value.length > CHAR_LIMIT;
  const canSend = !disabled && !overLimit && value.trim() !== "";

  // value'ya bağlı, tuş vuruşuna değil: yapıştırma da yazmakla aynı şekilde
  // kutuyu büyütüyor.
  useEffect(() => {
    const element = textareaRef.current;
    if (!element) return;
    element.style.height = "auto";
    element.style.height = `${Math.min(element.scrollHeight, MAX_TEXTAREA_HEIGHT)}px`;
  }, [value]);

  function handleKeyDown(event: KeyboardEvent<HTMLTextAreaElement>) {
    if (event.key !== "Enter" || event.shiftKey) return;
    event.preventDefault();
    if (canSend) onSend();
  }

  // Tasarımda varsayılan durumda çerçeve YOK, kenarı gölge tanımlıyor.
  // Çerçeve şeffaf duruyor ki focus ve hata durumunda kutu 2px zıplamasın.
  const borderClass = overLimit
    ? "border-red-500"
    : "border-transparent focus-within:border-brand-600";

  return (
    <div
      className={`rounded-16 border-2 bg-white px-4 py-3 shadow-normal ${borderClass}`}
    >
      <textarea
        ref={textareaRef}
        rows={2}
        value={value}
        onChange={(event) => onChange(event.target.value)}
        onKeyDown={handleKeyDown}
        placeholder={en.inputPlaceholder}
        /* maxLength BİLEREK yok: tasarım 801/800'ü hata olarak gösteriyor,
           yani limitin aşılmasına izin verilip uyarılıyor. */
        className="w-full resize-none text-body outline-none placeholder:text-neutral-400"
      />

      {overLimit && (
        <div className="mt-2 flex items-center gap-2 border-t border-neutral-200 pt-2 text-body-sm text-red-500">
          <AlertTriangleIcon className="size-4" />
          <span>{en.charLimitError}</span>
        </div>
      )}

      <div className="mt-1 flex items-end justify-end gap-3">
        <span
          className={`text-caption ${overLimit ? "text-red-500" : "text-neutral-500"}`}
        >
          {value.length || ""}/{CHAR_LIMIT}
        </span>
        <button
          type="button"
          onClick={onSend}
          disabled={!canSend}
          aria-label={en.a11y.send}
          className={`rounded-12 p-3 ${
            canSend ? "bg-brand-400 text-neutral-900" : "bg-neutral-100 text-neutral-300"
          }`}
        >
          <SendIcon />
        </button>
      </div>
    </div>
  );
}

export default MessageInput;
