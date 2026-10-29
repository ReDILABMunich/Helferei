import logo from "../assets/logo.png";
import type { en } from "../content/en";
import { CautionIcon, RefreshIcon } from "./icons";

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
          <CautionIcon className="w-10 text-red-600" />
          <div>
            <p>{content.error.title}</p>
            <p className="whitespace-pre-line">{content.error.body}</p>
          </div>
          <button
            type="button"
            onClick={onRetry}
            className="flex items-center gap-3 px-4 py-2 bg-red-50 border border-red-200 shadow-x-small rounded-8 text-h5 text-black hover:bg-red-100 active:bg-red-100"
          >
            {content.error.retry}
            <RefreshIcon className="w-6" />
          </button>
        </div>
      </div>
    </div>
  );
}

export default ErrorMessage;
