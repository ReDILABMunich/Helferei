import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import { en } from "../content/en";
import NewChatDialog from "./NewChatDialog";

describe("NewChatDialog", () => {
  it("is a dialog named by its title, shows the body and puts the focus on Cancel", () => {
    render(<NewChatDialog content={en} onConfirm={vi.fn()} onCancel={vi.fn()} />);

    const dialog = screen.getByRole("dialog", { name: en.newChat.title });
    expect(dialog).toHaveAttribute("aria-modal", "true");
    expect(screen.getByText(en.newChat.body)).toBeInTheDocument();
    expect(screen.getByRole("button", { name: en.newChat.cancel })).toHaveFocus();
  });

  it("Yes, Reset confirms", async () => {
    const user = userEvent.setup();
    const onConfirm = vi.fn();
    const onCancel = vi.fn();
    render(<NewChatDialog content={en} onConfirm={onConfirm} onCancel={onCancel} />);

    await user.click(screen.getByRole("button", { name: en.newChat.confirm }));

    expect(onConfirm).toHaveBeenCalledTimes(1);
    expect(onCancel).not.toHaveBeenCalled();
  });

  it("Cancel, the close icon, Escape and a click on the background cancel", async () => {
    const user = userEvent.setup();
    const onConfirm = vi.fn();
    const onCancel = vi.fn();
    render(<NewChatDialog content={en} onConfirm={onConfirm} onCancel={onCancel} />);

    await user.click(screen.getByRole("button", { name: en.newChat.cancel }));
    await user.click(screen.getByRole("button", { name: en.newChat.close }));
    await user.keyboard("{Escape}");
    await user.click(screen.getByRole("dialog").parentElement!);

    expect(onCancel).toHaveBeenCalledTimes(4);
    expect(onConfirm).not.toHaveBeenCalled();
  });

  it("a click inside the dialog does not cancel", async () => {
    const user = userEvent.setup();
    const onCancel = vi.fn();
    render(<NewChatDialog content={en} onConfirm={vi.fn()} onCancel={onCancel} />);

    await user.click(screen.getByText(en.newChat.body));

    expect(onCancel).not.toHaveBeenCalled();
  });
});
