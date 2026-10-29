import ReactMarkdown from "react-markdown";
import logo from "../assets/logo.png";
import { ArrowRightIcon } from "./icons";

type BotMessageProps = {
  text: string;
  breadcrumb?: string | null;
  onSegmentClick?: (path: string) => void;
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

function BotMessage({ text, breadcrumb = null, onSegmentClick }: BotMessageProps) {
  const segments = breadcrumb ? toSegments(breadcrumb) : [];

  return (
    <div className="flex gap-2 max-w-bubble">
      <div className="flex items-end">
        <img src={logo} alt="" className="w-6" />
      </div>
      <div className="flex-1 pb-3">
        <div className="flex flex-col gap-3 bg-white border-b-3 border-neutral-200 shadow-small rounded-t-20 rounded-br-20 px-5 py-3 text-blue-900">
          {/* Outside .bot-prose, so the markdown list styles do not apply. */}
          {segments.length > 0 && (
            <div className="pb-1 border-b-2 border-neutral-400">
              <ol data-testid="breadcrumb" className="flex flex-wrap items-center text-h5 drop-shadow-x-small">
                {segments.map((segment, index) => {
                  const last = index === segments.length - 1;
                  return (
                    <li key={index} className="flex items-center">
                      {last ? (
                        <span className="p-2 text-neutral-900">{segment}</span>
                      ) : (
                        <button
                          type="button"
                          className="p-2 text-blue-600 hover:text-brand-500 active:text-blue-900"
                          // The path up to and including this segment.
                          onClick={() => onSegmentClick?.(segments.slice(0, index + 1).join(" → "))}
                        >
                          {segment}
                        </button>
                      )}
                      {!last && <ArrowRightIcon className="w-5 text-black" />}
                    </li>
                  );
                })}
              </ol>
            </div>
          )}
          <div className="bot-prose">
            <ReactMarkdown>{bulletsToMarkdown(text)}</ReactMarkdown>
          </div>
        </div>
      </div>
    </div>
  );
}

export default BotMessage;
