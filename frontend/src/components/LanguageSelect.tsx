import { useState } from "react";
import type { KeyboardEvent } from "react";
import { languages } from "../content";
import type { en } from "../content/en";
import type { Language } from "../types";

type LanguageSelectProps = {
  content: typeof en;
  onChange: (code: Language) => void;
};

function LanguageSelect({ content, onChange }: LanguageSelectProps) {
  const [open, setOpen] = useState(false);

  function choose(code: Language) {
    onChange(code);
    setOpen(false);
  }

  function handleKeyDown(event: KeyboardEvent<HTMLDivElement>) {
    if (event.key === "Escape") setOpen(false);
  }

  return (
    <div onKeyDown={handleKeyDown} className="relative">
      <button
        type="button"
        aria-expanded={open}
        onClick={() => setOpen(!open)}
        className="flex items-center gap-4 p-2 bg-white"
      >
        <span className="flex items-center gap-4">
          {/* Placeholders until the icon library (FE-8). */}
          <svg viewBox="0 0 24 24" aria-hidden="true" className="w-6">
            <circle cx="12" cy="12" r="10" fill="none" stroke="currentColor" strokeWidth="1.5" />
            <path d="M2 12 H22 M12 2 C8 6 8 18 12 22 M12 2 C16 6 16 18 12 22" fill="none" stroke="currentColor" strokeWidth="1.5" />
          </svg>
          <span className="sr-only">{content.languageLabel}</span>
          <span className="font-bold text-h4 text-neutral-900">{content.short}</span>
        </span>
        <svg viewBox="0 0 12 8" aria-hidden="true" className="w-3">
          <path d="M1 1.5 L6 6.5 L11 1.5" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
        </svg>
      </button>
      {open && (
        <ul className="absolute right-0 top-full z-10 mt-2 flex flex-col gap-3 w-37.5 py-4 bg-white shadow-normal rounded-8">
          {languages.map((language) => (
            <li key={language.code}>
              <button
                type="button"
                aria-pressed={language.code === content.code}
                onClick={() => choose(language.code)}
                className="flex justify-between items-center gap-8 w-full p-3 font-bold text-h5 text-black hover:text-brand-500 focus-visible:text-brand-500"
              >
                {language.name}
                {language.code === content.code && (
                  <svg viewBox="0 0 24 17" aria-hidden="true" className="w-6">
                    <path d="M2 9 L8.5 15 L22 2" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
                  </svg>
                )}
              </button>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

export default LanguageSelect;
