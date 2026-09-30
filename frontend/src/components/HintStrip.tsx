import { ChevronsDownIcon, ChevronsUpIcon } from "./icons";
import { en } from "../content/en";

type HintStripProps = {
  open: boolean;
  onToggle: () => void;
};

// Figma "Hint strip" bileşeni:
//   Width      Fill, max 780px, min 326px
//   Padding    sol 8px  (şeridi input kutusundan içeri kaydıran şey bu)
// Figma "Hint" katmanı:
//   Fill       #E8EEFF  Color/Background/Information/Muted
//   Border     #BFD0FF  Color/Border/Information/Subtle-Low
//              üst 4px, sol 4px, sağ 1px, alt 1px  (asimetrik)
//   Radius     sol üst 0, diğer üçü 8px  (sekme sol üste oturuyor)
//   Padding    10px
//   Metin      Body-Small-Regular 14/145%, #4D4D4D
//
// Dört kenar ayrı ayrı veriliyor: border-x / border-y kullanmak border-t-4 ile
// aynı CSS özelliğini yazar ve hangisinin kazandığı sınıf sırasına kalır.
function HintStrip({ open, onToggle }: HintStripProps) {
  return (
    <div className="w-full min-w-[326px] max-w-[780px] pl-2">
      <button
        type="button"
        onClick={onToggle}
        aria-expanded={open}
        aria-label={open ? en.a11y.collapseHint : en.a11y.expandHint}
        className="w-fit rounded-t-8 bg-blue-100 px-4 py-2 text-neutral-900"
      >
        {open ? (
          <ChevronsDownIcon className="size-4" />
        ) : (
          <ChevronsUpIcon className="size-4" />
        )}
      </button>
      {open && (
        <p className="w-full rounded-8 rounded-tl-0 border-t-4 border-l-4 border-r border-b border-blue-100 bg-blue-50 p-2.5 text-body-sm text-neutral-700">
          {en.hint}
        </p>
      )}
    </div>
  );
}

export default HintStrip;
