import type { ReactNode } from "react";
import logo from "../assets/logo.png";
import logoGrey from "../assets/logo-gs.png";

// Noha'nın Components sayfasındaki ikon seti.
// Hepsi currentColor kullanır, yani rengi ebeveynin text-* class'ından alır.
// Hepsi aynı 24x24 viewBox ve aynı stroke ayarlarında, yan yana geldiklerinde
// optik olarak hizalı dursunlar diye.

type IconProps = { className?: string };

const BASE = "size-5 shrink-0";

function Glyph({ className = BASE, children }: IconProps & { children: ReactNode }) {
  return (
    <svg
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.8"
      strokeLinecap="round"
      strokeLinejoin="round"
      className={className}
      aria-hidden="true"
    >
      {children}
    </svg>
  );
}

export function SendIcon(props: IconProps) {
  return (
    <Glyph {...props}>
      <path d="M12 3 5 20l7-4 7 4z" />
    </Glyph>
  );
}

export function RefreshIcon(props: IconProps) {
  return (
    <Glyph {...props}>
      <path d="M20 12a8 8 0 1 1-2.3-5.6" />
      <path d="M20 4v4h-4" />
    </Glyph>
  );
}

export function AlertTriangleIcon(props: IconProps) {
  return (
    <Glyph {...props}>
      <path d="M12 4 2.5 20h19z" />
      <path d="M12 10v4" />
      <path d="M12 17.5v.5" />
    </Glyph>
  );
}

export function AlertCircleIcon(props: IconProps) {
  return (
    <Glyph {...props}>
      <circle cx="12" cy="12" r="9" />
      <path d="M12 7v6" />
      <path d="M12 16.5v.5" />
    </Glyph>
  );
}

export function ChevronsDownIcon(props: IconProps) {
  return (
    <Glyph {...props}>
      <path d="m6 8 6 5 6-5" />
      <path d="m6 14 6 5 6-5" />
    </Glyph>
  );
}

export function ChevronsUpIcon(props: IconProps) {
  return (
    <Glyph {...props}>
      <path d="m6 16 6-5 6 5" />
      <path d="m6 10 6-5 6 5" />
    </Glyph>
  );
}

export function ChevronsRightIcon(props: IconProps) {
  return (
    <Glyph {...props}>
      <path d="m8 6 5 6-5 6" />
      <path d="m14 6 5 6-5 6" />
    </Glyph>
  );
}

export function PlusIcon(props: IconProps) {
  return (
    <Glyph {...props}>
      <path d="M12 5v14" />
      <path d="M5 12h14" />
    </Glyph>
  );
}

export function CloseIcon(props: IconProps) {
  return (
    <Glyph {...props}>
      <path d="m6 6 12 12" />
      <path d="m18 6-12 12" />
    </Glyph>
  );
}

export function MenuIcon(props: IconProps) {
  return (
    <Glyph {...props}>
      <path d="M4 7h16" />
      <path d="M4 12h16" />
      <path d="M4 17h16" />
    </Glyph>
  );
}

export function CheckIcon(props: IconProps) {
  return (
    <Glyph {...props}>
      <path d="m5 13 4 4 10-10" />
    </Glyph>
  );
}

// Noha'nın Figma'dan export ettiği marka. Renkli hali balonlarda ve header'da,
// gri hali Thinking göstergesinde kullanılıyor.
//
// Görsel kare değil (1003x899), o yüzden boyutu SADECE genişlikten ver (w-7, w-10).
// size-7 gibi hem en hem boy veren bir class kullanırsan logo ezilir.
export function AtlasAvatar({
  className = "w-7",
  muted = false,
}: IconProps & { muted?: boolean }) {
  return (
    <img
      src={muted ? logoGrey : logo}
      alt=""
      aria-hidden="true"
      className={`${className} h-auto`}
    />
  );
}
