import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import { de } from "../content/de";
import { en } from "../content/en";
import MobileMenu from "./MobileMenu";

// The library name of each icon inside an element, in order.
const iconsIn = (element: HTMLElement) =>
  [...element.querySelectorAll("svg")].map((svg) => svg.getAttribute("data-icon"));

describe("MobileMenu", () => {
  it("the menu button opens the menu and tells screen readers", async () => {
    const user = userEvent.setup();
    render(<MobileMenu content={en} onLanguageChange={vi.fn()} onNewChat={vi.fn()} />);
    const menuButton = screen.getByRole("button", { name: "Open menu" });

    expect(menuButton).toHaveAttribute("aria-expanded", "false");
    expect(screen.queryByRole("button", { name: en.newChat.button })).not.toBeInTheDocument();

    await user.click(menuButton);

    expect(menuButton).toHaveAttribute("aria-expanded", "true");
    expect(screen.getByRole("button", { name: "Close menu" })).toBeInTheDocument();
    expect(screen.getByText(en.subtitle)).toBeInTheDocument();
    expect(screen.getByRole("button", { name: en.name })).toHaveAttribute("aria-pressed", "true");
    expect(screen.getByRole("button", { name: de.name })).toHaveAttribute("aria-pressed", "false");
    expect(screen.getByRole("button", { name: en.newChat.button })).toBeInTheDocument();
  });

  it("choosing a language reports it and closes the menu", async () => {
    const user = userEvent.setup();
    const onLanguageChange = vi.fn();
    render(<MobileMenu content={en} onLanguageChange={onLanguageChange} onNewChat={vi.fn()} />);

    await user.click(screen.getByRole("button", { name: "Open menu" }));
    await user.click(screen.getByRole("button", { name: de.name }));

    expect(onLanguageChange).toHaveBeenCalledWith("de");
    expect(screen.getByRole("button", { name: "Open menu" })).toHaveAttribute("aria-expanded", "false");
  });

  it("New chat reports it and closes the menu", async () => {
    const user = userEvent.setup();
    const onNewChat = vi.fn();
    render(<MobileMenu content={en} onLanguageChange={vi.fn()} onNewChat={onNewChat} />);

    await user.click(screen.getByRole("button", { name: "Open menu" }));
    await user.click(screen.getByRole("button", { name: en.newChat.button }));

    expect(onNewChat).toHaveBeenCalledOnce();
    expect(screen.getByRole("button", { name: "Open menu" })).toHaveAttribute("aria-expanded", "false");
  });

  it("the close button and Escape close the menu without changing anything", async () => {
    const user = userEvent.setup();
    const onLanguageChange = vi.fn();
    const onNewChat = vi.fn();
    render(<MobileMenu content={en} onLanguageChange={onLanguageChange} onNewChat={onNewChat} />);
    const menuButton = screen.getByRole("button", { name: "Open menu" });

    await user.click(menuButton);
    await user.click(screen.getByRole("button", { name: "Close menu" }));
    expect(menuButton).toHaveAttribute("aria-expanded", "false");

    await user.click(menuButton);
    await user.keyboard("{Escape}");
    expect(menuButton).toHaveAttribute("aria-expanded", "false");

    expect(onLanguageChange).not.toHaveBeenCalled();
    expect(onNewChat).not.toHaveBeenCalled();
  });

  it("shows the menu, close and tick icons from the library", async () => {
    const user = userEvent.setup();
    render(<MobileMenu content={en} onLanguageChange={vi.fn()} onNewChat={vi.fn()} />);
    const menuButton = screen.getByRole("button", { name: "Open menu" });

    expect(iconsIn(menuButton)).toEqual(["menu"]);

    await user.click(menuButton);
    expect(iconsIn(screen.getByRole("button", { name: "Close menu" }))).toEqual(["close"]);
    expect(iconsIn(screen.getByRole("button", { name: en.name }))).toEqual(["tick"]);
    expect(iconsIn(screen.getByRole("button", { name: de.name }))).toEqual([]);
  });
});
