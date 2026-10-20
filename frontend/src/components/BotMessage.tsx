import ReactMarkdown from "react-markdown";
import logo from "../assets/logo.png";

type BotMessageProps = {
  text: string;
};

// The backend marks list items with "•"; markdown needs "- ".
function bulletsToMarkdown(text: string): string {
  return text.replace(/^[ \t]*•[ \t]+/gm, "- ");
}

function BotMessage({ text }: BotMessageProps) {
  return (
    <div className="flex gap-2 max-w-bubble">
      <div className="flex items-end">
        <img src={logo} alt="" className="w-6" />
      </div>
      <div className="flex-1 pb-3">
        <div className="bot-prose bg-white border-b-3 border-neutral-200 shadow-small rounded-t-20 rounded-br-20 px-5 py-3 text-blue-900">
          <ReactMarkdown>{bulletsToMarkdown(text)}</ReactMarkdown>
        </div>
      </div>
    </div>
  );
}

export default BotMessage;
