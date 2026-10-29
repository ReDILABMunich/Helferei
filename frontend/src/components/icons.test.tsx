import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import * as icons from "./icons";

describe("icons", () => {
  it("every icon is hidden from screen readers, named after the library and takes the text colour", () => {
    for (const Icon of Object.values(icons)) {
      const { container } = render(<Icon />);
      const svg = container.querySelector("svg");

      expect(svg).toHaveAttribute("aria-hidden", "true");
      expect(svg).toHaveAttribute("data-icon");
      expect(svg).toHaveAttribute("fill", "currentColor");
    }
  });
});
