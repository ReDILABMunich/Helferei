import { useState } from "react";
import { en } from "../content/en";

function HintStrip() {
  const [open, setOpen] = useState(true);

  return (
    <div>
      <button
        type="button"
        aria-label={en.toggleHint}
        aria-expanded={open}
        onClick={() => setOpen(!open)}
      />
      {open && <p>{en.hint}</p>}
    </div>
  );
}

export default HintStrip;
