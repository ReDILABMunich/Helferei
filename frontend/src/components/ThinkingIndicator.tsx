import logoGs from "../assets/logo-gs.png";
import { en } from "../content/en";

function ThinkingIndicator() {
  return (
    <div className="flex justify-center items-center py-5">
      <img src={logoGs} alt="" className="w-6" />
      <div className="flex items-end gap-2 px-3 py-5">
        <p className="text-body text-neutral-500">{en.thinking}</p>
        <span aria-hidden="true" className="flex items-end gap-0.5 pb-1.5">
          <span className="atlas-dot size-0.75 rounded-full bg-neutral-500" />
          <span className="atlas-dot size-0.75 rounded-full bg-neutral-500" />
          <span className="atlas-dot size-0.75 rounded-full bg-neutral-500" />
          <span className="atlas-dot size-0.75 rounded-full bg-neutral-500" />
        </span>
      </div>
    </div>
  );
}

export default ThinkingIndicator;
