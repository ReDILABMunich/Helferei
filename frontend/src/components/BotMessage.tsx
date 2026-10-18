import ReactMarkdown from "react-markdown";

type BotMessageProps = {
  text: string;
};

// The backend marks list items with "•"; markdown needs "- ".
function bulletsToMarkdown(text: string): string {
  return text.replace(/^[ \t]*•[ \t]+/gm, "- ");
}

function BotMessage({ text }: BotMessageProps) {
  return <ReactMarkdown>{bulletsToMarkdown(text)}</ReactMarkdown>;
}

export default BotMessage;
