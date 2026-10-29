import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import BotMessage from "./BotMessage";

describe("BotMessage", () => {
  it("shows lines that start with • as a list", () => {
    render(<BotMessage text={"You need:\n• Vorname\n• Nachname\n• Geburtsdatum"} />);

    const items = screen.getAllByRole("listitem");
    expect(items.map((item) => item.textContent)).toEqual(["Vorname", "Nachname", "Geburtsdatum"]);
  });
});
