import logo from "../assets/logo.png";
import type { en } from "../content/en";
import type { Language } from "../types";
import LanguageSelect from "./LanguageSelect";

type AppHeaderProps = {
  content: typeof en;
  onLanguageChange: (code: Language) => void;
  onNewChat: () => void;
};

function AppHeader({ content, onLanguageChange, onNewChat }: AppHeaderProps) {
  return (
    <header className="bg-white border-b-2 border-neutral-200 py-5">
      <div className="mx-auto max-w-content flex justify-between items-center">
        <div className="flex flex-col items-start flex-1">
          <div className="flex items-center gap-4">
            <img src={logo} alt="" className="w-12" />
            <h1 className="font-display font-bold text-h2 text-black">{content.title}</h1>
          </div>
          <p className="self-stretch font-bold text-body text-neutral-700">{content.subtitle}</p>
        </div>
        <div className="flex justify-end items-center gap-5">
          <LanguageSelect content={content} onChange={onLanguageChange} />
          <button type="button" aria-label={content.newChat.button} onClick={onNewChat}>
            {/* Placeholder until the icon library (FE-8). */}
            <svg viewBox="0 0 24 24" aria-hidden="true" className="w-6" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round">
              <rect x="3" y="3" width="18" height="18" rx="3" />
              <path d="M12 8 V16 M8 12 H16" />
            </svg>
          </button>
        </div>
      </div>
    </header>
  );
}

export default AppHeader;
