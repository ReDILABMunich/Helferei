import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import { de } from "../content/de";
import { en } from "../content/en";
import MessageInput from "./MessageInput";

// The library name of each icon inside an element, in order.
const iconsIn = (element: HTMLElement) =>
  [...element.querySelectorAll("svg")].map((svg) => svg.getAttribute("data-icon"));

describe("MessageInput", () => {
  it("sends the text with the send button and clears the box", async () => {
    const user = userEvent.setup();
    const onSend = vi.fn();
    render(<MessageInput content={en} onSend={onSend} sending={false} />);

    await user.type(screen.getByRole("textbox"), "What is a Steuernummer?");
    await user.click(screen.getByRole("button", { name: en.send }));

    expect(onSend).toHaveBeenCalledWith("What is a Steuernummer?");
    expect(screen.getByRole("textbox")).toHaveValue("");
  });

  it("does not send an empty box or only spaces", async () => {
    const user = userEvent.setup();
    const onSend = vi.fn();
    render(<MessageInput content={en} onSend={onSend} sending={false} />);

    await user.click(screen.getByRole("button", { name: en.send }));
    await user.type(screen.getByRole("textbox"), "   ");
    await user.click(screen.getByRole("button", { name: en.send }));

    expect(onSend).not.toHaveBeenCalled();
  });

  it("shows /800 when the box is empty", () => {
    render(<MessageInput content={en} onSend={vi.fn()} sending={false} />);

    expect(screen.getByText("/800")).toBeInTheDocument();
  });

  it("over the limit marks the box as invalid and disables the send button", async () => {
    const user = userEvent.setup();
    render(<MessageInput content={en} onSend={vi.fn()} sending={false} />);

    await user.click(screen.getByRole("textbox"));
    await user.paste("a".repeat(801));

    expect(screen.getByRole("textbox")).toHaveAttribute("aria-invalid", "true");
    expect(screen.getByRole("button", { name: en.send })).toBeDisabled();
  });

  it("does not send with Enter over the limit and keeps the text", async () => {
    const user = userEvent.setup();
    const onSend = vi.fn();
    render(<MessageInput content={en} onSend={onSend} sending={false} />);

    await user.click(screen.getByRole("textbox"));
    await user.paste("a".repeat(801));
    await user.keyboard("{Enter}");

    expect(onSend).not.toHaveBeenCalled();
    expect(screen.getByRole("textbox")).toHaveValue("a".repeat(801));
  });

  it("removes the error and sends again after deleting back to 800", async () => {
    const user = userEvent.setup();
    const onSend = vi.fn();
    render(<MessageInput content={en} onSend={onSend} sending={false} />);

    await user.click(screen.getByRole("textbox"));
    await user.paste("a".repeat(801));
    await user.keyboard("{Backspace}");

    expect(screen.getByText("800/800")).toBeInTheDocument();
    expect(screen.queryByText(en.tooLong)).not.toBeInTheDocument();
    await user.click(screen.getByRole("button", { name: en.send }));
    expect(onSend).toHaveBeenCalledWith("a".repeat(800));
  });

  it("shows /800 again after sending", async () => {
    const user = userEvent.setup();
    render(<MessageInput content={en} onSend={vi.fn()} sending={false} />);

    await user.type(screen.getByRole("textbox"), "What is a Steuernummer?{Enter}");

    expect(screen.getByText("/800")).toBeInTheDocument();
  });

  it("shows the error in the new language when the language changes", async () => {
    const user = userEvent.setup();
    const { rerender } = render(<MessageInput content={en} onSend={vi.fn()} sending={false} />);

    await user.click(screen.getByRole("textbox"));
    await user.paste("a".repeat(801));
    rerender(<MessageInput content={de} onSend={vi.fn()} sending={false} />);

    expect(screen.getByText(de.tooLong)).toBeInTheDocument();
    expect(screen.getByRole("textbox")).toHaveValue("a".repeat(801));
  });

  it("over the limit shows the caution icon next to the error", async () => {
    const user = userEvent.setup();
    render(<MessageInput content={en} onSend={vi.fn()} sending={false} />);

    await user.click(screen.getByRole("textbox"));
    await user.paste("a".repeat(801));

    expect(iconsIn(screen.getByText(en.tooLong))).toEqual(["caution"]);
  });
});
