import { useState } from "react";
import { languages } from "../content";
import type { en } from "../content/en";
import type { Language } from "../types";

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

  return (
    <div>
      <button type="button" aria-label={content.menu.open} aria-expanded={open} onClick={() => setOpen(true)}>
        {/* Placeholder until the icon library (FE-8). */}
        <svg viewBox="0 0 48 34" aria-hidden="true" className="w-12">
          <path d="M2 3 H46 M2 17 H46 M2 31 H46" stroke="currentColor" strokeWidth="3" strokeLinecap="round" />
        </svg>
      </button>
      {open && (
        <div>
          <button type="button" aria-label={content.menu.close} />
          <p>{content.subtitle}</p>
          <ul>
            {languages.map((language) => (
              <li key={language.code}>
                <button
                  type="button"
                  aria-pressed={language.code === content.code}
                  onClick={() => chooseLanguage(language.code)}
                >
                  {language.name}
                </button>
              </li>
            ))}
          </ul>
          <button type="button" onClick={startNewChat}>
            {content.newChat.button}
          </button>
        </div>
      )}
    </div>
  );
}

export default MobileMenu;
