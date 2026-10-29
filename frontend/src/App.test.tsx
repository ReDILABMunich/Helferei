import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import App from "./App";
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
