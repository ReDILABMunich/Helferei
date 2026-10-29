import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it } from "vitest";
import { en } from "../content/en";
import HintStrip from "./HintStrip";

describe("HintStrip", () => {
  it("is open when the app starts", () => {
    render(<HintStrip />);

    expect(screen.getByText(en.hint)).toBeInTheDocument();
    expect(screen.getByRole("button", { name: en.toggleHint })).toHaveAttribute("aria-expanded", "true");
  });

  it("hides the hint with the toggle and shows it again", async () => {
    const user = userEvent.setup();
    render(<HintStrip />);
    const toggle = screen.getByRole("button", { name: en.toggleHint });

    await user.click(toggle);
    expect(screen.queryByText(en.hint)).not.toBeInTheDocument();
    expect(toggle).toHaveAttribute("aria-expanded", "false");

    await user.click(toggle);
    expect(screen.getByText(en.hint)).toBeInTheDocument();
    expect(toggle).toHaveAttribute("aria-expanded", "true");
  });
});
