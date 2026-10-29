import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import { en } from "../content/en";
import MessageInput from "./MessageInput";

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
});
