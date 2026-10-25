import { useState } from "react";
import type { KeyboardEvent } from "react";
import logo from "../assets/logo.png";
import { languages } from "../content";
import type { en } from "../content/en";
import type { Language } from "../types";
import { CloseIcon, MenuIcon, TickIcon } from "./icons";

type MobileMenuProps = {
  content: typeof en;
  onLanguageChange: (code: Language) => void;
  onNewChat: () => void;
};

function MobileMenu({ content, onLanguageChange, onNewChat }: MobileMenuProps) {
  const [open, setOpen] = useState(false);

  function chooseLanguage(code: Language) {
    onLanguageChange(code);
    setOpen(false);
  }

  function startNewChat() {
    onNewChat();
    setOpen(false);
  }

  function handleKeyDown(event: KeyboardEvent<HTMLDivElement>) {
    if (event.key === "Escape") setOpen(false);
  }

  return (
    <div onKeyDown={handleKeyDown} className="tablet:hidden">
      <button type="button" aria-label={content.menu.open} aria-expanded={open} onClick={() => setOpen(true)} className="flex text-black">
        <MenuIcon className="w-12" />
      </button>
      {open && (
        <div className="fixed inset-0 z-10 flex flex-col gap-8 py-5 bg-white overflow-y-auto">
          <div className="flex flex-col gap-4 py-2">
            <div className="flex justify-between items-center px-5">
              <div className="flex items-center gap-4">
                <img src={logo} alt="" className="w-12" />
                <span className="font-display font-bold text-h2 text-black">{content.title}</span>
              </div>
              <button
                type="button"
                aria-label={content.menu.close}
                onClick={() => setOpen(false)}
                className="flex justify-center items-center size-10 p-2.5 text-black"
              >
                <CloseIcon className="w-6" />
              </button>
            </div>
            <p className="pl-5 pr-15 font-bold text-body text-neutral-700">{content.subtitle}</p>
            <hr className="border-t-2 border-neutral-200" />
          </div>
          <div className="flex flex-col gap-10 px-5 py-4">
            <ul className="flex flex-col gap-5">
              {languages.map((language) => (
                <li key={language.code}>
                  <button
                    type="button"
                    aria-pressed={language.code === content.code}
                    onClick={() => chooseLanguage(language.code)}
                    className="flex justify-between items-center w-full p-2 rounded-8 font-bold text-h5 text-neutral-900"
                  >
                    {language.name}
                    {language.code === content.code && <TickIcon className="w-7.5" />}
                  </button>
                </li>
              ))}
            </ul>
            <div className="flex flex-col gap-6">
              <hr className="border-t-2 border-neutral-200" />
              <button type="button" onClick={startNewChat} className="flex w-full p-2 rounded-8 font-bold text-h5 text-neutral-900">
                {content.newChat.button}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default MobileMenu;
