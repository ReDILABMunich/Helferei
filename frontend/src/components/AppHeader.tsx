import logo from "../assets/logo.png";
import { en } from "../content/en";

function AppHeader() {
  return (
    <header className="bg-white border-b-2 border-neutral-200 py-5">
      <div className="mx-auto max-w-content flex justify-between items-center">
        <div className="flex flex-col items-start flex-1">
          <div className="flex items-center gap-4">
            <img src={logo} alt="" className="w-12" />
            <h1 className="font-display font-bold text-h2 text-black">{en.title}</h1>
          </div>
          <p className="self-stretch font-bold text-body text-neutral-700">{en.subtitle}</p>
        </div>
      </div>
    </header>
  );
}

export default AppHeader;
