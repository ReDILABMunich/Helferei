import { useState } from "react";
import type { KeyboardEvent } from "react";
import { languages } from "../content";
import type { en } from "../content/en";
import type { Language } from "../types";
import { ArrowDownIcon, GlobeIcon, TickIcon } from "./icons";

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
          <GlobeIcon className="w-6" />
          <span className="sr-only">{content.languageLabel}</span>
          <span className="font-bold text-h4 text-neutral-900">{content.short}</span>
        </span>
        <ArrowDownIcon className="w-3" />
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
                {language.code === content.code && <TickIcon className="w-6" />}
              </button>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

export default LanguageSelect;
