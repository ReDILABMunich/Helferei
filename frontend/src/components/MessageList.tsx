import Message from "./Message";
import type { Message as MessageType } from "../types";

type MessageListProps = {
  messages: MessageType[];
};

function MessageList({ messages }: MessageListProps) {
  return (
    <div className="message-list">
      {messages.map((message, index) => (
        <Message key={index} message={message} />
      ))}
    </div>
  );
}

export default MessageList;
