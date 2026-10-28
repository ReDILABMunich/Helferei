import { render, screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import App from "./App";
import { de } from "./content/de";
import { en } from "./content/en";

// The backend is replaced by a fetch the test controls: each call waits until
// the test answers it, so the loading state can be checked in between.
type Pending = {
  body: { message: string; session_id: string | null; lang: string };
  respond: (r: Response) => void;
};
let pending: Pending[];

function answer(index: number, body: unknown, status = 200) {
  pending[index].respond(
    new Response(JSON.stringify(body), {
      status,
      headers: { "Content-Type": "application/json" },
    }),
  );
}

beforeEach(() => {
  pending = [];
  vi.stubGlobal(
    "fetch",
    vi.fn(
      (_url: string, init: RequestInit) =>
        new Promise<Response>((respond) => {
          pending.push({ body: JSON.parse(init.body as string), respond });
        }),
    ),
  );
});

afterEach(() => {
  vi.unstubAllGlobals();
});

describe("FE-1 acceptance criteria", () => {
  it("normal path: asks a question, shows the answer and continues the conversation", async () => {
    const user = userEvent.setup();
    render(<App />);
    const welcomeFirstLine = en.welcome.split("\n")[0].replace(/\\$/, "");
    expect(screen.getByText(welcomeFirstLine, { exact: false })).toBeInTheDocument();

    await user.type(
      screen.getByRole("textbox"),
      "What is a Steuernummer?{Enter}",
    );

    expect(screen.getByText("What is a Steuernummer?")).toBeInTheDocument();
    expect(screen.getByText(en.thinking)).toBeInTheDocument();

    answer(0, {
      answer: "A Steuernummer is your tax number.",
      session_id: "abc",
      breadcrumb: "",
    });

    expect(
      await screen.findByText("A Steuernummer is your tax number."),
    ).toBeInTheDocument();
    expect(screen.queryByText(en.thinking)).not.toBeInTheDocument();

    await user.type(screen.getByRole("textbox"), "Where do I find it?{Enter}");
    await waitFor(() => expect(pending).toHaveLength(2));
    expect(pending[1].body.session_id).toBe("abc");
  });

  it("something goes wrong: shows an error, keeps the question and the session", async () => {
    const user = userEvent.setup();
    render(<App />);

    await user.type(screen.getByRole("textbox"), "First question{Enter}");
    answer(0, { answer: "First answer", session_id: "abc", breadcrumb: "" });
    await screen.findByText("First answer");

    await user.type(screen.getByRole("textbox"), "Second question{Enter}");
    answer(1, { detail: "AI request failed" }, 502);

    expect(await screen.findByText(en.error.title)).toBeInTheDocument();
    expect(screen.queryByText(en.thinking)).not.toBeInTheDocument();
    expect(screen.getByText("Second question")).toBeInTheDocument();

    await user.type(screen.getByRole("textbox"), "Third question{Enter}");
    await waitFor(() => expect(pending).toHaveLength(3));
    expect(screen.queryByText(en.error.title)).not.toBeInTheDocument();
    expect(pending[2].body.session_id).toBe("abc");
  });
});

describe("FE-2 acceptance criteria", () => {
  it("normal path: choosing Deutsch shows the interface in German and sends the question in German", async () => {
    const user = userEvent.setup();
    render(<App />);

    await user.click(screen.getByRole("button", { name: /Language/ }));
    await user.click(screen.getByRole("button", { name: de.name }));

    expect(screen.getByText(de.subtitle)).toBeInTheDocument();
    const welcomeFirstLine = de.welcome.split("\n")[0].replace(/\\$/, "");
    expect(screen.getByText(welcomeFirstLine, { exact: false })).toBeInTheDocument();
    expect(screen.getByPlaceholderText(de.inputPlaceholder)).toBeInTheDocument();
    expect(screen.getByText(de.hint)).toBeInTheDocument();
    expect(screen.getByText(de.disclaimer)).toBeInTheDocument();

    await user.type(screen.getByRole("textbox"), "Was ist eine Steuernummer?{Enter}");
    await waitFor(() => expect(pending).toHaveLength(1));
    expect(pending[0].body.lang).toBe("de");
  });

  it("something goes wrong: the error message is in German", async () => {
    const user = userEvent.setup();
    render(<App />);

    await user.click(screen.getByRole("button", { name: /Language/ }));
    await user.click(screen.getByRole("button", { name: de.name }));
    await user.type(screen.getByRole("textbox"), "Erste Frage{Enter}");
    answer(0, { detail: "AI request failed" }, 502);

    expect(await screen.findByText(de.error.title)).toBeInTheDocument();
  });

  it("the loading indicator is in German", async () => {
    const user = userEvent.setup();
    render(<App />);

    await user.click(screen.getByRole("button", { name: /Language/ }));
    await user.click(screen.getByRole("button", { name: de.name }));
    await user.type(screen.getByRole("textbox"), "Erste Frage{Enter}");

    expect(screen.getByText(de.thinking)).toBeInTheDocument();
  });

  it("switching back to English shows English again, sets the page language and sends in English", async () => {
    const user = userEvent.setup();
    render(<App />);

    await user.click(screen.getByRole("button", { name: /Language/ }));
    await user.click(screen.getByRole("button", { name: de.name }));
    expect(document.documentElement.lang).toBe("de");

    await user.click(screen.getByRole("button", { name: /Sprache/ }));
    await user.click(screen.getByRole("button", { name: en.name }));

    expect(screen.getByText(en.subtitle)).toBeInTheDocument();
    expect(document.documentElement.lang).toBe("en");

    await user.type(screen.getByRole("textbox"), "What is a Steuernummer?{Enter}");
    await waitFor(() => expect(pending).toHaveLength(1));
    expect(pending[0].body.lang).toBe("en");
  });
});

describe("FE-3 acceptance criteria", () => {
  it("normal path: Try again sends the same question with the same session and shows the answer", async () => {
    const user = userEvent.setup();
    render(<App />);

    await user.type(screen.getByRole("textbox"), "First question{Enter}");
    answer(0, { answer: "First answer", session_id: "abc", breadcrumb: "" });
    await screen.findByText("First answer");

    await user.type(screen.getByRole("textbox"), "Second question{Enter}");
    answer(1, { detail: "AI request failed" }, 502);
    const alert = await screen.findByRole("alert");

    await user.click(within(alert).getByRole("button", { name: en.error.retry }));
    await waitFor(() => expect(pending).toHaveLength(3));
    expect(pending[2].body.message).toBe("Second question");
    expect(pending[2].body.session_id).toBe("abc");

    answer(2, { answer: "Second answer", session_id: "abc", breadcrumb: "" });
    expect(await screen.findByText("Second answer")).toBeInTheDocument();
    expect(screen.getAllByText("Second question")).toHaveLength(1);
  });

  it("something goes wrong: when Try again fails too, the error and the button come back", async () => {
    const user = userEvent.setup();
    render(<App />);

    await user.type(screen.getByRole("textbox"), "First question{Enter}");
    answer(0, { detail: "AI request failed" }, 502);
    let alert = await screen.findByRole("alert");

    await user.click(within(alert).getByRole("button", { name: en.error.retry }));
    await waitFor(() => expect(pending).toHaveLength(2));
    expect(screen.queryByRole("alert")).not.toBeInTheDocument();
    answer(1, { detail: "AI request failed" }, 502);

    alert = await screen.findByRole("alert");
    expect(within(alert).getByRole("button", { name: en.error.retry })).toBeInTheDocument();
    expect(screen.getAllByText("First question")).toHaveLength(1);
  });
});

describe("FE-6 acceptance criteria", () => {
  it("normal path: the counter shows the number of characters out of 800", async () => {
    const user = userEvent.setup();
    render(<App />);

    await user.type(screen.getByRole("textbox"), "What is a Steuernummer?");

    expect(screen.getByText("23/800")).toBeInTheDocument();
  });

  it("something goes wrong: over the limit the counter shows it, the error is shown and nothing is sent", async () => {
    const user = userEvent.setup();
    render(<App />);

    await user.click(screen.getByRole("textbox"));
    await user.paste("a".repeat(900));
    await user.click(screen.getByRole("button", { name: en.send }));

    expect(screen.getByText("900/800")).toBeInTheDocument();
    expect(screen.getByText(en.tooLong)).toBeInTheDocument();
    expect(pending).toHaveLength(0);
  });
});

describe("FE-10 acceptance criteria", () => {
  it("normal path: typing removes the empty error", async () => {
    const user = userEvent.setup();
    render(<App />);
    await user.click(screen.getByRole("button", { name: en.send }));
    expect(screen.getByText("Please type a question before sending")).toBeInTheDocument();

    await user.type(screen.getByRole("textbox"), "W");

    expect(screen.queryByText("Please type a question before sending")).not.toBeInTheDocument();
    expect(screen.getByRole("textbox")).not.toBeInvalid();
  });

  it("something goes wrong: sending an empty box shows the error and sends nothing", async () => {
    const user = userEvent.setup();
    render(<App />);

    await user.click(screen.getByRole("button", { name: en.send }));

    expect(screen.getByText("Please type a question before sending")).toBeInTheDocument();
    expect(screen.getByRole("textbox")).toBeInvalid();
    expect(pending).toHaveLength(0);
  });
});

describe("FE-4 acceptance criteria", () => {
  it("normal path: confirming a new chat leaves only the welcome message and drops the session", async () => {
    const user = userEvent.setup();
    render(<App />);

    await user.type(screen.getByRole("textbox"), "First question{Enter}");
    answer(0, { answer: "First answer", session_id: "abc", breadcrumb: "" });
    await screen.findByText("First answer");

    await user.click(screen.getByRole("button", { name: en.newChat.button }));
    const dialog = screen.getByRole("dialog", { name: en.newChat.title });
    await user.click(within(dialog).getByRole("button", { name: en.newChat.confirm }));

    expect(screen.queryByRole("dialog")).not.toBeInTheDocument();
    expect(screen.queryByText("First question")).not.toBeInTheDocument();
    expect(screen.queryByText("First answer")).not.toBeInTheDocument();
    const welcomeFirstLine = en.welcome.split("\n")[0].replace(/\\$/, "");
    expect(screen.getByText(welcomeFirstLine, { exact: false })).toBeInTheDocument();

    await user.type(screen.getByRole("textbox"), "Second question{Enter}");
    await waitFor(() => expect(pending).toHaveLength(2));
    expect(pending[1].body.session_id).toBeNull();
  });

  it("something goes wrong: cancelling keeps the conversation and the session", async () => {
    const user = userEvent.setup();
    render(<App />);

    await user.type(screen.getByRole("textbox"), "First question{Enter}");
    answer(0, { answer: "First answer", session_id: "abc", breadcrumb: "" });
    await screen.findByText("First answer");

    await user.click(screen.getByRole("button", { name: en.newChat.button }));
    const dialog = screen.getByRole("dialog", { name: en.newChat.title });
    await user.click(within(dialog).getByRole("button", { name: en.newChat.cancel }));

    expect(screen.queryByRole("dialog")).not.toBeInTheDocument();
    expect(screen.getByText("First question")).toBeInTheDocument();
    expect(screen.getByText("First answer")).toBeInTheDocument();

    await user.type(screen.getByRole("textbox"), "Second question{Enter}");
    await waitFor(() => expect(pending).toHaveLength(2));
    expect(pending[1].body.session_id).toBe("abc");
  });

  it("confirming clears the text box", async () => {
    const user = userEvent.setup();
    render(<App />);

    await user.type(screen.getByRole("textbox"), "Half a question");
    await user.click(screen.getByRole("button", { name: en.newChat.button }));
    await user.click(screen.getByRole("button", { name: en.newChat.confirm }));

    expect(screen.getByRole("textbox")).toHaveValue("");
  });

  it("the language stays German after a new chat", async () => {
    const user = userEvent.setup();
    render(<App />);

    await user.click(screen.getByRole("button", { name: /Language/ }));
    await user.click(screen.getByRole("button", { name: de.name }));
    await user.type(screen.getByRole("textbox"), "Erste Frage{Enter}");
    answer(0, { answer: "Erste Antwort", session_id: "abc", breadcrumb: "" });
    await screen.findByText("Erste Antwort");

    await user.click(screen.getByRole("button", { name: de.newChat.button }));
    await user.click(screen.getByRole("button", { name: de.newChat.confirm }));

    const welcomeFirstLine = de.welcome.split("\n")[0].replace(/\\$/, "");
    expect(screen.getByText(welcomeFirstLine, { exact: false })).toBeInTheDocument();

    await user.type(screen.getByRole("textbox"), "Zweite Frage{Enter}");
    await waitFor(() => expect(pending).toHaveLength(2));
    expect(pending[1].body.lang).toBe("de");
    expect(pending[1].body.session_id).toBeNull();
  });
});

// The library name of each icon inside an element, in order.
const iconsIn = (element: HTMLElement) =>
  [...element.querySelectorAll("svg")].map((svg) => svg.getAttribute("data-icon"));

describe("FE-8 acceptance criteria", () => {
  it("normal path: every icon is the library icon", async () => {
    const user = userEvent.setup();
    render(<App />);

    expect(iconsIn(screen.getByRole("button", { name: en.newChat.button }))).toEqual(["doc-add"]);
    expect(iconsIn(screen.getByRole("button", { name: en.menu.open }))).toEqual(["menu"]);
    expect(iconsIn(screen.getByRole("button", { name: /Language/ }))).toEqual(["globe", "arrow-single-down"]);
    expect(iconsIn(screen.getByRole("button", { name: en.toggleHint }))).toEqual(["arrow-single-down"]);
    expect(iconsIn(screen.getByRole("button", { name: en.send }))).toEqual(["navigation"]);

    await user.type(screen.getByRole("textbox"), "First question{Enter}");
    answer(0, { detail: "AI request failed" }, 502);
    expect(iconsIn(await screen.findByRole("alert"))).toEqual(["caution", "refresh"]);

    await user.click(screen.getByRole("button", { name: en.newChat.button }));
    expect(iconsIn(screen.getByRole("dialog", { name: en.newChat.title }))).toEqual(["close", "info"]);
  });

  it("something goes wrong: in German, every button that shows only an icon has its German label", async () => {
    const user = userEvent.setup();
    render(<App />);
    await user.click(screen.getByRole("button", { name: /Language/ }));
    await user.click(screen.getByRole("button", { name: de.name }));

    // No visible text, one library icon, and the German label as its name.
    const expectIconOnly = (button: HTMLElement) => {
      expect(button.textContent).toBe("");
      expect(iconsIn(button)).toHaveLength(1);
      expect(iconsIn(button)[0]).not.toBeNull();
    };
    expectIconOnly(screen.getByRole("button", { name: de.newChat.button }));
    expectIconOnly(screen.getByRole("button", { name: de.toggleHint }));
    expectIconOnly(screen.getByRole("button", { name: de.send }));

    await user.click(screen.getByRole("button", { name: de.menu.open }));
    expectIconOnly(screen.getByRole("button", { name: de.menu.open }));
    expectIconOnly(screen.getByRole("button", { name: de.menu.close }));
    await user.click(screen.getByRole("button", { name: de.menu.close }));

    await user.click(screen.getByRole("button", { name: de.newChat.button }));
    expectIconOnly(screen.getByRole("button", { name: de.newChat.close }));
  });
});

// The breadcrumb bars on the screen, and the segments of one bar in order.
const breadcrumbBars = () => screen.queryAllByTestId("breadcrumb");
const segmentsIn = (bar: HTMLElement) =>
  within(bar).getAllByRole("listitem").map((item) => item.textContent);

describe("FE-5 acceptance criteria", () => {
  it("normal path: the breadcrumb shows in segments above the answer text", async () => {
    const user = userEvent.setup();
    render(<App />);

    await user.type(screen.getByRole("textbox"), "What should I enter for Art der Tätigkeit?{Enter}");
    answer(0, {
      answer: "Type of Business Activity.",
      session_id: "abc",
      breadcrumb: "Section 1: Allgemeine Angaben → Art der Tätigkeit",
    });
    const answerText = await screen.findByText("Type of Business Activity.");

    const bars = breadcrumbBars();
    expect(bars).toHaveLength(1);
    expect(segmentsIn(bars[0])).toEqual(["Section 1", "Allgemeine Angaben", "Art der Tätigkeit"]);
    expect(bars[0].compareDocumentPosition(answerText)).toBe(Node.DOCUMENT_POSITION_FOLLOWING);
  });

  it("something goes wrong: an empty breadcrumb shows no bar", async () => {
    const user = userEvent.setup();
    render(<App />);

    await user.type(screen.getByRole("textbox"), "Thanks{Enter}");
    answer(0, { answer: "You're welcome.", session_id: "abc", breadcrumb: "" });
    await screen.findByText("You're welcome.");

    expect(breadcrumbBars()).toHaveLength(0);
  });

  it("with Deutsch selected, the German breadcrumb from the backend is shown", async () => {
    const user = userEvent.setup();
    render(<App />);

    await user.click(screen.getByRole("button", { name: /Language/ }));
    await user.click(screen.getByRole("button", { name: de.name }));
    await user.type(screen.getByRole("textbox"), "Was ist Art der Tätigkeit?{Enter}");
    await waitFor(() => expect(pending).toHaveLength(1));
    expect(pending[0].body.lang).toBe("de");
    answer(0, {
      answer: "Art der Tätigkeit beschreibt Ihre Tätigkeit.",
      session_id: "abc",
      breadcrumb: "Abschnitt 1: Allgemeine Angaben → Art der Tätigkeit",
    });
    await screen.findByText("Art der Tätigkeit beschreibt Ihre Tätigkeit.");

    expect(segmentsIn(breadcrumbBars()[0])).toEqual(["Abschnitt 1", "Allgemeine Angaben", "Art der Tätigkeit"]);
  });

  it("each answer keeps its own breadcrumb", async () => {
    const user = userEvent.setup();
    render(<App />);

    await user.type(screen.getByRole("textbox"), "First question{Enter}");
    answer(0, { answer: "First answer", session_id: "abc", breadcrumb: "Section 1: Allgemeine Angaben" });
    await screen.findByText("First answer");
    await user.type(screen.getByRole("textbox"), "Second question{Enter}");
    await waitFor(() => expect(pending).toHaveLength(2));
    answer(1, { answer: "Second answer", session_id: "abc", breadcrumb: "Section 9: Betriebsstätten" });
    await screen.findByText("Second answer");

    expect(breadcrumbBars().map(segmentsIn)).toEqual([
      ["Section 1", "Allgemeine Angaben"],
      ["Section 9", "Betriebsstätten"],
    ]);
  });
});

describe("FE-15 acceptance criteria", () => {
  it("normal path: clicking a segment sends its path as my question", async () => {
    const user = userEvent.setup();
    render(<App />);

    await user.type(screen.getByRole("textbox"), "What should I enter for Art der Tätigkeit?{Enter}");
    answer(0, {
      answer: "Type of Business Activity.",
      session_id: "abc",
      breadcrumb: "Section 1: Allgemeine Angaben → Art der Tätigkeit",
    });
    await screen.findByText("Type of Business Activity.");

    await user.click(within(breadcrumbBars()[0]).getByRole("button", { name: "Allgemeine Angaben" }));

    expect(screen.getByText("Section 1 → Allgemeine Angaben")).toBeInTheDocument();
    await waitFor(() => expect(pending).toHaveLength(2));
    expect(pending[1].body.message).toBe("Section 1 → Allgemeine Angaben");
    expect(pending[1].body.session_id).toBe("abc");
    answer(1, { answer: "General information.", session_id: "abc", breadcrumb: "Section 1: Allgemeine Angaben" });
    await screen.findByText("General information.");
    expect(segmentsIn(breadcrumbBars()[1])).toEqual(["Section 1", "Allgemeine Angaben"]);
  });

  it("something goes wrong: a click while an answer is loading sends nothing", async () => {
    const user = userEvent.setup();
    render(<App />);

    await user.type(screen.getByRole("textbox"), "What should I enter for Art der Tätigkeit?{Enter}");
    answer(0, {
      answer: "Type of Business Activity.",
      session_id: "abc",
      breadcrumb: "Section 1: Allgemeine Angaben → Art der Tätigkeit",
    });
    await screen.findByText("Type of Business Activity.");
    await user.type(screen.getByRole("textbox"), "Second question{Enter}");
    await waitFor(() => expect(pending).toHaveLength(2));

    await user.click(within(breadcrumbBars()[0]).getByRole("button", { name: "Allgemeine Angaben" }));

    expect(pending).toHaveLength(2);
    expect(screen.queryByText("Section 1 → Allgemeine Angaben")).not.toBeInTheDocument();
  });
});

// The last bot answer, and the texts shown in blue-900 inside it, in order.
const lastAnswer = () => [...document.querySelectorAll(".bot-prose")].at(-1)!;
const blueIn = (answer: Element) => [...answer.querySelectorAll(".text-blue-900")].map((el) => el.textContent);

describe("FE-13 acceptance criteria", () => {
  it("normal path: the German field names are blue-900 and the rest of the answer is neutral-900", async () => {
    const user = userEvent.setup();
    render(<App />);

    await user.type(screen.getByRole("textbox"), "Section 9{Enter}");
    answer(0, {
      answer:
        "Section 9 'Betriebsstätten' · Business Premises — asks about additional business premises.\n\n" +
        "In this section, you will provide information about:\n" +
        "• Bezeichnung der Betriebsstätte · Name/Description of Business Premise — description and address of each location.",
      session_id: "abc",
      breadcrumb: "Section 9: Betriebsstätten",
    });
    await screen.findByText(/asks about additional business premises/);

    expect(blueIn(lastAnswer())).toEqual(["Betriebsstätten", "Bezeichnung der Betriebsstätte"]);
    expect(lastAnswer().closest(".text-neutral-900")).not.toBeNull();
  });

  it("something goes wrong: a list item with neither · nor — has nothing in blue-900", async () => {
    const user = userEvent.setup();
    render(<App />);

    await user.type(screen.getByRole("textbox"), "Section 9{Enter}");
    answer(0, {
      answer: "You need:\n• Bezeichnung der Betriebsstätte\n• Geburtsdatum · Date of Birth — date of birth",
      session_id: "abc",
      breadcrumb: "",
    });
    await screen.findByText("Bezeichnung der Betriebsstätte");

    expect(blueIn(lastAnswer())).toEqual(["Geburtsdatum"]);
    expect(lastAnswer().closest(".text-neutral-900")).not.toBeNull();
  });
});

describe("FE-14 acceptance criteria", () => {
  // jsdom has no scrollIntoView, so each call saves what was on screen and
  // whether the scrolled element is the last one in the chat.
  type Scroll = { text: string; isLast: boolean };
  let scrolls: Scroll[];
  const original = Element.prototype.scrollIntoView;

  afterEach(() => {
    Element.prototype.scrollIntoView = original;
  });

  beforeEach(() => {
    scrolls = [];
    Element.prototype.scrollIntoView = vi.fn(function (this: Element) {
      scrolls.push({
        text: document.querySelector("main")?.textContent ?? "",
        isLast: this.closest("main") !== null && this.nextElementSibling === null,
      });
    });
  });

  function lastScroll() {
    expect(scrolls.length).toBeGreaterThan(0);
    const scroll = scrolls[scrolls.length - 1];
    expect(scroll.isLast).toBe(true);
    return scroll.text;
  }

  it("normal path: scrolls to the end after the question and again after the answer", async () => {
    const user = userEvent.setup();
    render(<App />);

    await user.type(screen.getByRole("textbox"), "What is a Steuernummer?{Enter}");
    expect(lastScroll()).toContain("What is a Steuernummer?");
    expect(lastScroll()).toContain(en.thinking);

    answer(0, { answer: "A Steuernummer is your tax number.", session_id: "abc", breadcrumb: "" });
    await screen.findByText("A Steuernummer is your tax number.");
    expect(lastScroll()).toContain("A Steuernummer is your tax number.");
  });

  it("something goes wrong: scrolls to the end after the error message is shown", async () => {
    const user = userEvent.setup();
    render(<App />);

    await user.type(screen.getByRole("textbox"), "First question{Enter}");
    answer(0, { detail: "AI request failed" }, 502);
    await screen.findByRole("alert");

    expect(lastScroll()).toContain(en.error.title);
    expect(lastScroll()).toContain(en.error.retry);
  });

  it("Try again scrolls to the end when the loading indicator replaces the error", async () => {
    const user = userEvent.setup();
    render(<App />);

    await user.type(screen.getByRole("textbox"), "First question{Enter}");
    answer(0, { detail: "AI request failed" }, 502);
    const alert = await screen.findByRole("alert");
    await user.click(within(alert).getByRole("button", { name: en.error.retry }));

    expect(lastScroll()).toContain(en.thinking);
    expect(lastScroll()).not.toContain(en.error.title);
  });

  it("switching the language does not scroll", async () => {
    const user = userEvent.setup();
    render(<App />);
    await user.type(screen.getByRole("textbox"), "First question{Enter}");
    answer(0, { answer: "First answer", session_id: "abc", breadcrumb: "" });
    await screen.findByText("First answer");
    const before = scrolls.length;

    await user.click(screen.getByRole("button", { name: /Language/ }));
    await user.click(screen.getByRole("button", { name: de.name }));

    expect(scrolls).toHaveLength(before);
  });
});
