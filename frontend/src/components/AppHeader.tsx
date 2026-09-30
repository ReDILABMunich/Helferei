import { AtlasAvatar, PlusIcon } from "./icons";
import { en } from "../content/en";

type AppHeaderProps = {
  onNewChat: () => void;
};

// md altında gizlenir; orada MobileMenu devralır (Task 6).
function AppHeader({ onNewChat }: AppHeaderProps) {
  return (
    <header className="hidden border-b border-neutral-100 bg-white md:block">
      <div className="mx-auto flex max-w-[1012px] items-start justify-between px-5 py-4 lg:px-8">
        <div className="flex items-center gap-3">
          <AtlasAvatar className="w-10" />
          <div>
            <p className="font-display text-h2 font-bold leading-none">{en.appName}</p>
            <p className="mt-1 text-body-sm text-neutral-700">{en.tagline}</p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <span className="border-b-2 border-brand-500 text-body font-bold text-neutral-900">
            {en.language.en}
          </span>
          <span aria-hidden="true" className="text-neutral-200">
            |
          </span>
          <span
            aria-disabled="true"
            aria-label={en.a11y.switchToGerman}
            className="cursor-not-allowed text-body text-neutral-400"
          >
            {en.language.de}
          </span>
          <button
            type="button"
            onClick={onNewChat}
            aria-label={en.a11y.newChat}
            className="rounded-8 border border-neutral-900 p-1 text-neutral-900"
          >
            <PlusIcon className="size-4" />
          </button>
        </div>
      </div>
    </header>
  );
}

export default AppHeader;
