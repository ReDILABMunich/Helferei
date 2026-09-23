import ReactMarkdown from "react-markdown";
import type { Message as MessageType } from "../types";

type MessageProps = {
  message: MessageType;
};

function Message({ message }: MessageProps) {
  return (
    <div className="message">
      <strong>{message.role}:</strong>
      {message.role === "bot" ? (
        <ReactMarkdown>{message.text}</ReactMarkdown>
      ) : (
        <span> {message.text}</span>
      )}
    </div>
  );
}

export default Message;
