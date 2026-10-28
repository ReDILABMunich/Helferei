import { render, screen, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import BotMessage from "./BotMessage";

// The segments of the breadcrumb bar in order, and the library icons in it.
const segments = () =>
  within(screen.getByTestId("breadcrumb")).getAllByRole("listitem").map((item) => item.textContent);
const icons = () =>
  [...screen.getByTestId("breadcrumb").querySelectorAll("svg")].map((svg) => svg.getAttribute("data-icon"));

describe("BotMessage", () => {
  it("shows lines that start with • as a list", () => {
    render(<BotMessage text={"You need:\n• Vorname\n• Nachname\n• Geburtsdatum"} />);

    const items = screen.getAllByRole("listitem");
    expect(items.map((item) => item.textContent)).toEqual(["Vorname", "Nachname", "Geburtsdatum"]);
  });

  it("shows no breadcrumb bar without a breadcrumb", () => {
    render(<BotMessage text="Welcome" />);

    expect(screen.queryByTestId("breadcrumb")).not.toBeInTheDocument();
  });

  it("splits only the first segment at its colon, trims spaces and drops empty segments", () => {
    render(<BotMessage text="Answer" breadcrumb=" Section 3: Kontakt →  → Telefon: privat " />);

    expect(segments()).toEqual(["Section 3", "Kontakt", "Telefon: privat"]);
  });

  it("puts an arrow-right icon between two segments", () => {
    render(<BotMessage text="Answer" breadcrumb="Section 1: Allgemeine Angaben → Art der Tätigkeit" />);

    expect(icons()).toEqual(["arrow-right", "arrow-right"]);
  });

  it("shows a breadcrumb with one segment and no colon without an arrow", () => {
    render(<BotMessage text="Answer" breadcrumb="Allgemeine Angaben" />);

    expect(segments()).toEqual(["Allgemeine Angaben"]);
    expect(icons()).toEqual([]);
  });

  it("makes every segment but the last a button", () => {
    render(<BotMessage text="Answer" breadcrumb="Section 1: Allgemeine Angaben → Art der Tätigkeit" onSegmentClick={() => {}} />);

    const buttons = within(screen.getByTestId("breadcrumb")).getAllByRole("button");
    expect(buttons.map((button) => button.textContent)).toEqual(["Section 1", "Allgemeine Angaben"]);
  });

  it("clicking the first segment sends no arrow", async () => {
    const onSegmentClick = vi.fn();
    render(<BotMessage text="Answer" breadcrumb="Section 1: Allgemeine Angaben → Art der Tätigkeit" onSegmentClick={onSegmentClick} />);

    await userEvent.click(screen.getByRole("button", { name: "Section 1" }));

    expect(onSegmentClick).toHaveBeenCalledWith("Section 1");
  });
});

// The texts shown in blue-900 inside the answer text, in order.
const blueNames = () =>
  [...document.querySelectorAll(".bot-prose .text-blue-900")].map((el) => el.textContent);

describe("BotMessage field names", () => {
  it("a German list item has the text before — as its name", () => {
    render(<BotMessage text={"Sie brauchen:\n• Geburtsdatum — Ihr Geburtsdatum"} />);

    expect(blueNames()).toEqual(["Geburtsdatum"]);
  });

  it("a first line that starts with Abschnitt has the quoted text as its name", () => {
    render(<BotMessage text="Abschnitt 9 'Betriebsstätten' behandelt weitere Betriebsstätten." />);

    expect(blueNames()).toEqual(["Betriebsstätten"]);
  });

  it("a first line that starts with a quote has the quoted text as its name", () => {
    render(<BotMessage text="'Geburtsdatum' · Date of Birth — is the field where you enter your date of birth." />);

    expect(blueNames()).toEqual(["Geburtsdatum"]);
  });

  it("a first line that quotes the user's words has no name", () => {
    render(<BotMessage text={"I found several matching 'gebusdatum' in:\n• Geburtsdatum · Date of Birth — date of birth"} />);

    expect(blueNames()).toEqual(["Geburtsdatum"]);
  });

  it("a name with - is blue up to the ·", () => {
    render(
      <BotMessage
        text={
          "It includes:\n• Adresse - nur anzugeben, falls von Adresse der steuerpflichtigen Person abweichend · Address - only if different — only fill if needed"
        }
      />,
    );

    expect(blueNames()).toEqual(["Adresse - nur anzugeben, falls von Adresse der steuerpflichtigen Person abweichend"]);
  });

  it("the quotes in the navigation tip are not names", () => {
    render(
      <BotMessage
        text={
          "You need:\n• Geburtsdatum · Date of Birth — date of birth\n\n🧭 To navigate the form, type a section number or the GERMAN name of a section, subsection, or field — e.g. '7', 'Kleinunternehmer-Regelung', or 'Geburtsdatum'."
        }
      />,
    );

    expect(blueNames()).toEqual(["Geburtsdatum"]);
  });
});
