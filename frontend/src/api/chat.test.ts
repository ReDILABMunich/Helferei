import { afterEach, describe, expect, it, vi } from "vitest";
import { sendChat } from "./chat";

function jsonResponse(body: unknown, status = 200) {
  return new Response(JSON.stringify(body), {
    status,
    headers: { "Content-Type": "application/json" },
  });
}

afterEach(() => {
  vi.unstubAllGlobals();
});

describe("sendChat", () => {
  it("posts the message, session id and language to /chat and returns the reply", async () => {
    const fetchMock = vi.fn().mockResolvedValue(
      jsonResponse({ answer: "An answer", session_id: "abc", breadcrumb: "Section 1" }),
    );
    vi.stubGlobal("fetch", fetchMock);

    const reply = await sendChat({ message: "Hi", session_id: null, lang: "en" });

    const [url, init] = fetchMock.mock.calls[0];
    expect(url).toMatch(/\/chat$/);
    expect(init.method).toBe("POST");
    expect(JSON.parse(init.body)).toEqual({ message: "Hi", session_id: null, lang: "en" });
    expect(reply).toEqual({ answer: "An answer", session_id: "abc", breadcrumb: "Section 1" });
  });

  it("throws when the backend returns a status that is not 2xx", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(jsonResponse({ detail: "error" }, 502)));

    await expect(sendChat({ message: "Hi", session_id: null, lang: "en" })).rejects.toThrow();
  });

  it("throws when the network fails", async () => {
    vi.stubGlobal("fetch", vi.fn().mockRejectedValue(new TypeError("Failed to fetch")));

    await expect(sendChat({ message: "Hi", session_id: null, lang: "en" })).rejects.toThrow();
  });
});
