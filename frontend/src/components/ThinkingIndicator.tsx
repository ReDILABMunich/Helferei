import { AtlasAvatar } from "./icons";
import { en } from "../content/en";

const DELAYS = ["0ms", "160ms", "320ms", "480ms"];

function ThinkingIndicator() {
  return (
    <div className="flex items-center justify-center gap-2" aria-live="polite">
      <AtlasAvatar className="w-6" muted />
      <span className="text-body text-neutral-500">{en.thinking}</span>
      <span className="flex items-center gap-1">
        {DELAYS.map((delay) => (
          <span
            key={delay}
            style={{ animationDelay: delay }}
            className="atlas-dot size-1.5 rounded-1000 bg-neutral-500"
          />
        ))}
      </span>
    </div>
  );
}

export default ThinkingIndicator;
