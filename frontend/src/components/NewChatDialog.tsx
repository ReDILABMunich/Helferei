import { useId } from "react";
import type { en } from "../content/en";

type NewChatDialogProps = {
  content: typeof en;
  onConfirm: () => void;
  onCancel: () => void;
};

function NewChatDialog({ content, onConfirm, onCancel }: NewChatDialogProps) {
  const titleId = useId();

  return (
    <div>
      <div role="dialog" aria-modal="true" aria-labelledby={titleId}>
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
