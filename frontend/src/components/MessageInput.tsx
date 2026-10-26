import { useState } from "react";
import type { KeyboardEvent } from "react";
import type { en } from "../content/en";
import { CautionIcon, NavigationIcon } from "./icons";

const MAX_LENGTH = 800;

type MessageInputProps = {
  content: typeof en;
  onSend: (text: string) => void;
  sending: boolean;
};

function MessageInput({ content, onSend, sending }: MessageInputProps) {
  const [text, setText] = useState("");
  const [empty, setEmpty] = useState(false);
  const tooLong = text.length > MAX_LENGTH;

  function submit() {
    if (sending || tooLong) return;
    if (text.trim() === "") {
      setEmpty(true);
      return;
    }
    onSend(text);
    setText("");
  }

  function handleKeyDown(event: KeyboardEvent<HTMLTextAreaElement>) {
    if (event.key !== "Enter" || event.shiftKey) return;
    event.preventDefault();
    submit();
  }

  return (
    <div className={`flex items-end pt-2 pr-3 pb-3 pl-2 bg-white border-3 rounded-8 ${tooLong || empty ? "border-red-500" : "border-brand-500"}`}>
      <div className="flex-1 min-w-0 flex flex-col pt-3 px-3">
        <textarea
          className="w-full min-h-9.5 field-sizing-content resize-none outline-none text-body placeholder:text-neutral-300"
          value={text}
          onChange={(event) => {
            setText(event.target.value);
            setEmpty(false);
          }}
          onKeyDown={handleKeyDown}
          placeholder={content.inputPlaceholder}
          aria-invalid={tooLong || empty}
        />
        <div className={`flex justify-between items-end ${tooLong ? "mt-3 pt-3 border-t border-neutral-700" : empty ? "pt-3" : "h-6"}`}>
          {(tooLong || empty) && (
            <p className="flex gap-2 pl-3 text-body text-red-600">
              <CautionIcon className="w-7 shrink-0" />
              {tooLong ? content.tooLong : content.empty}
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
        className="flex justify-center items-center w-14 h-12 px-4 py-3 bg-brand-500 rounded-8 enabled:hover:bg-brand-400 enabled:active:bg-brand-500 disabled:bg-neutral-100 disabled:text-neutral-300"
      >
        <NavigationIcon className="w-6" />
      </button>
    </div>
  );
}

export default MessageInput;
