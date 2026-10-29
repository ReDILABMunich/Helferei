import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import { de } from "../content/de";
import { en } from "../content/en";
import LanguageSelect from "./LanguageSelect";

describe("LanguageSelect", () => {
  it("opens and closes the list with the button and tells screen readers", async () => {
    const user = userEvent.setup();
    render(<LanguageSelect content={en} onChange={vi.fn()} />);
    const button = screen.getByRole("button", { name: /Language/ });

    expect(button).toHaveAttribute("aria-expanded", "false");
    expect(screen.queryByRole("list")).not.toBeInTheDocument();

    await user.click(button);
    expect(button).toHaveAttribute("aria-expanded", "true");
    expect(screen.getByRole("list")).toBeInTheDocument();

    await user.click(button);
    expect(button).toHaveAttribute("aria-expanded", "false");
    expect(screen.queryByRole("list")).not.toBeInTheDocument();
  });

  it("shows every language by name and marks the current one", async () => {
    const user = userEvent.setup();
    render(<LanguageSelect content={en} onChange={vi.fn()} />);

    expect(screen.getByRole("button", { name: /Language/ })).toHaveTextContent(en.short);
    await user.click(screen.getByRole("button", { name: /Language/ }));

    expect(screen.getByRole("button", { name: en.name })).toHaveAttribute("aria-pressed", "true");
    expect(screen.getByRole("button", { name: de.name })).toHaveAttribute("aria-pressed", "false");
  });

  it("choosing a language reports it and closes the list", async () => {
    const user = userEvent.setup();
    const onChange = vi.fn();
    render(<LanguageSelect content={en} onChange={onChange} />);

    await user.click(screen.getByRole("button", { name: /Language/ }));
    await user.click(screen.getByRole("button", { name: de.name }));

    expect(onChange).toHaveBeenCalledWith("de");
    expect(screen.queryByRole("list")).not.toBeInTheDocument();
  });

  it("Escape closes the list without changing the language", async () => {
    const user = userEvent.setup();
    const onChange = vi.fn();
    render(<LanguageSelect content={en} onChange={onChange} />);

    await user.click(screen.getByRole("button", { name: /Language/ }));
    await user.keyboard("{Escape}");

    expect(screen.queryByRole("list")).not.toBeInTheDocument();
    expect(onChange).not.toHaveBeenCalled();
  });
});
