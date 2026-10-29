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
