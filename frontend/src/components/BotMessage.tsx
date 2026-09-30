import ReactMarkdown from "react-markdown";
import { AtlasAvatar } from "./icons";

type BotMessageProps = {
  text: string;
};

// Backend markdown döndürüyor ama madde işareti olarak "•" (U+2022) kullanıyor.
// Markdown bunu liste saymaz (sadece -, *, + sayar), üstelik satırlar tek \n ile
// ayrıldığı için hepsi tek paragrafa yapışıyor. Satır başındaki • işaretlerini
// gerçek markdown listesine çeviriyoruz.
//
// GEÇİCİ: kalıcı çözüm backend'de. Basant "- " döndürdüğü an bu fonksiyon silinir.
// Sadece satır başındaki • hedefleniyor; metin içinde ayırıcı olarak kullanılan
// "·" (Anrede · Salutation) karakterine dokunulmuyor.
function bulletsToMarkdown(text: string): string {
  return text.replace(/^[ \t]*•[ \t]+/gm, "- ");
}

// Sütunun sol kenarına hizalanan şey kart değil, avatar. Kart avatara yer
// açmak için içeriden başlıyor; avatar kartın dışında, sol altta duruyor.
function BotMessage({ text }: BotMessageProps) {
  return (
    <div className="relative max-w-full pb-3 pl-8 md:max-w-[95%] lg:max-w-[91%]">
      <div className="bot-prose rounded-24 rounded-bl-0 bg-white px-5 py-3 shadow-normal">
        <ReactMarkdown>{bulletsToMarkdown(text)}</ReactMarkdown>
      </div>
      <AtlasAvatar className="absolute bottom-0 left-0 w-7" />
    </div>
  );
}

export default BotMessage;
