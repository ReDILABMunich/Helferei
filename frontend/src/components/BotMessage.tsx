import ReactMarkdown from "react-markdown";
import logo from "../assets/logo.png";
import { ArrowRightIcon } from "./icons";

type BotMessageProps = {
  text: string;
  breadcrumb?: string | null;
};

// The backend marks list items with "•"; markdown needs "- ".
function bulletsToMarkdown(text: string): string {
  return text.replace(/^[ \t]*•[ \t]+/gm, "- ");
}

// "Section 1: Allgemeine Angaben → Art der Tätigkeit" becomes three segments.
// Only the first segment is split at ": ", field names can contain one.
function toSegments(breadcrumb: string): string[] {
  const [first, ...rest] = breadcrumb.split("→").map((part) => part.trim()).filter(Boolean);
  if (!first) return [];
  const colon = first.indexOf(": ");
  const head = colon === -1 ? [first] : [first.slice(0, colon), first.slice(colon + 2)];
  return [...head, ...rest];
}

function BotMessage({ text, breadcrumb = null }: BotMessageProps) {
  const segments = breadcrumb ? toSegments(breadcrumb) : [];

  return (
    <div className="flex gap-2 max-w-bubble">
      <div className="flex items-end">
        <img src={logo} alt="" className="w-6" />
      </div>
      <div className="flex-1 pb-3">
        <div className="bot-prose bg-white border-b-3 border-neutral-200 shadow-small rounded-t-20 rounded-br-20 px-5 py-3 text-blue-900">
          {segments.length > 0 && (
            <ol data-testid="breadcrumb">
              {segments.map((segment, index) => (
                <li key={index}>
                  {segment}
                  {index < segments.length - 1 && <ArrowRightIcon className="w-5" />}
                </li>
              ))}
            </ol>
          )}
          <ReactMarkdown>{bulletsToMarkdown(text)}</ReactMarkdown>
        </div>
      </div>
    </div>
  );
}

export default BotMessage;
