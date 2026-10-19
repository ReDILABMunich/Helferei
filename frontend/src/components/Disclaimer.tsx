import type { en } from "../content/en";

type DisclaimerProps = {
  content: typeof en;
};

function Disclaimer({ content }: DisclaimerProps) {
  return <p className="text-center text-footnote text-neutral-700">{content.disclaimer}</p>;
}

export default Disclaimer;
