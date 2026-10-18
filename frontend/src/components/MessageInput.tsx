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
    <div>
      <textarea
        value={text}
        onChange={(event) => setText(event.target.value)}
        onKeyDown={handleKeyDown}
        placeholder={en.inputPlaceholder}
      />
      <button type="button" onClick={submit}>
        {en.send}
      </button>
    </div>
  );
}

export default MessageInput;
