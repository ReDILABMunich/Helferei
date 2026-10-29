import { useState } from "react";
import type { en } from "../content/en";
import { ArrowDownIcon, ArrowUpIcon } from "./icons";

type HintStripProps = {
  content: typeof en;
};

function HintStrip({ content }: HintStripProps) {
  const [open, setOpen] = useState(true);

  return (
    <div className="flex flex-col items-start pl-1 max-w-246">
      <button
        type="button"
        aria-label={content.toggleHint}
        aria-expanded={open}
        onClick={() => setOpen(!open)}
        className="flex justify-center items-center w-12 pt-2 px-1 pb-1 bg-blue-100 border-3 border-b-0 border-blue-100 rounded-t-8"
      >
        {open ? <ArrowDownIcon className="w-3" /> : <ArrowUpIcon className="w-3" />}
      </button>
      {open && (
        <p className="self-stretch px-1 py-2 border border-t-4 border-l-4 border-blue-100 rounded-8 rounded-tl-0 text-body-sm text-neutral-700">
          {content.hint}
        </p>
      )}
    </div>
  );
}

export default HintStrip;
