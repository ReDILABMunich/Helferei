import type { en } from "../content/en";
import type { Message } from "../types";
import BotMessage from "./BotMessage";
import UserMessage from "./UserMessage";

type MessageListProps = {
  content: typeof en;
  messages: Message[];
  onSend: (text: string) => void;
};

function MessageList({ content, messages, onSend }: MessageListProps) {
  return (
    <div className="flex flex-col gap-2 tablet:gap-3">
      <BotMessage text={content.welcome} />
      {messages.map((message) =>
        message.role === "bot" ? (
          <BotMessage key={message.id} text={message.text} breadcrumb={message.breadcrumb} onSegmentClick={onSend} />
        ) : (
          <UserMessage key={message.id} text={message.text} />
        ),
      )}
    </div>
  );
}

export default MessageList;
