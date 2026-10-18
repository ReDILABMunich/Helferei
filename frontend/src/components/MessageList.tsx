import { en } from "../content/en";
import type { Message } from "../types";
import BotMessage from "./BotMessage";
import UserMessage from "./UserMessage";

type MessageListProps = {
  messages: Message[];
};

function MessageList({ messages }: MessageListProps) {
  return (
    <div>
      <BotMessage text={en.welcome} />
      {messages.map((message) =>
        message.role === "bot" ? (
          <BotMessage key={message.id} text={message.text} />
        ) : (
          <UserMessage key={message.id} text={message.text} />
        ),
      )}
    </div>
  );
}

export default MessageList;
