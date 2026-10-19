import logo from "../assets/logo.png";
import type { en } from "../content/en";
import type { Language } from "../types";
import LanguageSelect from "./LanguageSelect";

type AppHeaderProps = {
  content: typeof en;
  onLanguageChange: (code: Language) => void;
};

function AppHeader({ content, onLanguageChange }: AppHeaderProps) {
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
        </div>
      </div>
    </header>
  );
}

export default AppHeader;
