import logo from "../assets/logo.png";
import type { en } from "../content/en";

type ErrorMessageProps = {
  content: typeof en;
  onRetry: () => void;
};

function ErrorMessage({ content, onRetry }: ErrorMessageProps) {
  return (
    <div className="flex gap-2 py-1 min-w-75 max-w-150 self-start">
      <div className="flex items-end">
        <img src={logo} alt="" className="w-6" />
      </div>
      <div className="flex-1 py-3">
        <div
          role="alert"
          className="flex flex-col justify-center items-center gap-5 px-4 py-5 bg-red-50 border-b-3 border-red-500 shadow-small rounded-8 rounded-bl-0 text-center text-neutral-900"
        >
          {/* Placeholder until the icon library (FE-8). */}
          <svg viewBox="0 0 40 34" aria-hidden="true" className="w-10 text-red-600">
            <path d="M20 2 L38 32 H2 Z" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinejoin="round" />
            <path d="M20 12 V22" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" />
            <circle cx="20" cy="27" r="1.5" fill="currentColor" />
          </svg>
          <div>
            <p>{content.error.title}</p>
            <p className="whitespace-pre-line">{content.error.body}</p>
          </div>
          <button type="button" onClick={onRetry}>
            {content.error.retry}
          </button>
        </div>
      </div>
    </div>
  );
}

export default ErrorMessage;
