import logo from "../assets/logo.png";
import type { en } from "../content/en";
import type { Language } from "../types";
import LanguageSelect from "./LanguageSelect";
import MobileMenu from "./MobileMenu";

type AppHeaderProps = {
  content: typeof en;
  onLanguageChange: (code: Language) => void;
  onNewChat: () => void;
};

function AppHeader({ content, onLanguageChange, onNewChat }: AppHeaderProps) {
  return (
    <header className="bg-white border-b-2 border-neutral-200 px-5 desktop:px-8 py-5">
      <div className="mx-auto max-w-content flex justify-between items-center">
        <div className="flex flex-col items-start flex-1">
          <div className="flex items-center gap-4">
            <img src={logo} alt="" className="w-12" />
            <h1 className="font-display font-bold text-h2 text-black">{content.title}</h1>
          </div>
          <p className="hidden tablet:block self-stretch font-bold text-body text-neutral-700">{content.subtitle}</p>
        </div>
        <MobileMenu content={content} onLanguageChange={onLanguageChange} onNewChat={onNewChat} />
        <div className="hidden tablet:flex justify-end items-center gap-5">
          <LanguageSelect content={content} onChange={onLanguageChange} />
          <button type="button" aria-label={content.newChat.button} onClick={onNewChat} className="text-black">
            {/* Placeholder until the icon library (FE-8). */}
            <svg viewBox="0 0 28 33.52" aria-hidden="true" className="w-7" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
              <path d="M18 1 H4 A3 3 0 0 0 1 4 V29.5 A3 3 0 0 0 4 32.5 H24 A3 3 0 0 0 27 29.5 V10 Z" />
              <path d="M18 1 V10 H27" />
              <path d="M14 15 V25 M9 20 H19" />
            </svg>
          </button>
        </div>
      </div>
    </header>
  );
}

export default AppHeader;
