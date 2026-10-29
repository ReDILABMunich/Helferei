import { act, renderHook } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { sendChat } from "../api/chat";
import type { ChatReply, Language } from "../types";
import { useChat } from "./useChat";

vi.mock("../api/chat", () => ({ sendChat: vi.fn() }));
const sendChatMock = vi.mocked(sendChat);

// A promise the test resolves or rejects by hand, so it can look at the "sending" state before the reply arrives.
function deferred<T>() {
  let resolve!: (value: T) => void;
  let reject!: (reason: unknown) => void;
  const promise = new Promise<T>((res, rej) => {
    resolve = res;
    reject = rej;
  });
  return { promise, resolve, reject };
}

const reply = (session_id: string): ChatReply => ({
  answer: `Answer for ${session_id}`,
  session_id,
  breadcrumb: "",
});

beforeEach(() => {
  sendChatMock.mockReset();
});

describe("useChat", () => {
  it("starts idle with no messages", () => {
    const { result } = renderHook(() => useChat("en"));

    expect(result.current.status).toBe("idle");
    expect(result.current.messages).toEqual([]);
  });

  it("idle -> sending: adds the question and sends it without a session id", () => {
    sendChatMock.mockReturnValue(deferred<ChatReply>().promise);
    const { result } = renderHook(() => useChat("en"));

    act(() => result.current.send("What is a Steuernummer?"));

    expect(result.current.status).toBe("sending");
    expect(result.current.messages.at(-1)).toMatchObject({
      role: "user",
      text: "What is a Steuernummer?",
    });
    expect(sendChatMock).toHaveBeenCalledWith({
      message: "What is a Steuernummer?",
      session_id: null,
      lang: "en",
    });
  });

  it("sending -> idle: adds the answer and uses its session id for the next question", async () => {
    const first = deferred<ChatReply>();
    sendChatMock
      .mockReturnValueOnce(first.promise)
      .mockReturnValueOnce(deferred<ChatReply>().promise);
    const { result } = renderHook(() => useChat("en"));

    act(() => result.current.send("First"));
    await act(async () => first.resolve(reply("abc")));

    expect(result.current.status).toBe("idle");
    expect(result.current.messages.at(-1)).toMatchObject({
      role: "bot",
      text: "Answer for abc",
    });

    act(() => result.current.send("Second"));
    expect(sendChatMock).toHaveBeenLastCalledWith({
      message: "Second",
      session_id: "abc",
      lang: "en",
    });
  });

  it("sending -> failed: keeps the question and the session id", async () => {
    const first = deferred<ChatReply>();
    const second = deferred<ChatReply>();
    sendChatMock
      .mockReturnValueOnce(first.promise)
      .mockReturnValueOnce(second.promise)
      .mockReturnValueOnce(deferred<ChatReply>().promise);
    const { result } = renderHook(() => useChat("en"));

    act(() => result.current.send("First"));
    await act(async () => first.resolve(reply("abc")));
    act(() => result.current.send("Second"));
    await act(async () => second.reject(new Error("502")));

    expect(result.current.status).toBe("failed");
    expect(result.current.messages.at(-1)).toMatchObject({
      role: "user",
      text: "Second",
    });

    act(() => result.current.send("Third"));
    expect(result.current.status).toBe("sending");
    expect(sendChatMock).toHaveBeenLastCalledWith({
      message: "Third",
      session_id: "abc",
      lang: "en",
    });
  });

  it("sending -> sending: ignores a second send, even in the same tick", () => {
    sendChatMock.mockReturnValue(deferred<ChatReply>().promise);
    const { result } = renderHook(() => useChat("en"));

    act(() => {
      result.current.send("Once");
      result.current.send("Once");
    });
    act(() => result.current.send("Again"));

    expect(sendChatMock).toHaveBeenCalledTimes(1);
    expect(result.current.messages).toHaveLength(1);
  });

  it("ignores empty text and text with only spaces", () => {
    const { result } = renderHook(() => useChat("en"));

    act(() => result.current.send(""));
    act(() => result.current.send("   "));

    expect(sendChatMock).not.toHaveBeenCalled();
    expect(result.current.status).toBe("idle");
    expect(result.current.messages).toEqual([]);
  });

  it("a new language keeps the messages and the session, and is sent with the next question", async () => {
    const first = deferred<ChatReply>();
    sendChatMock
      .mockReturnValueOnce(first.promise)
      .mockReturnValueOnce(deferred<ChatReply>().promise);
    const { result, rerender } = renderHook(({ lang }) => useChat(lang), {
      initialProps: { lang: "en" as Language },
    });

    act(() => result.current.send("First"));
    await act(async () => first.resolve(reply("abc")));
    rerender({ lang: "de" });

    expect(result.current.messages).toHaveLength(2);

    act(() => result.current.send("Zweite"));
    expect(sendChatMock).toHaveBeenLastCalledWith({
      message: "Zweite",
      session_id: "abc",
      lang: "de",
    });
  });
});

describe("useChat retry (FE-3)", () => {
  it("failed -> sending: sends the last question again with the session id, without a new message", async () => {
    const first = deferred<ChatReply>();
    const second = deferred<ChatReply>();
    sendChatMock
      .mockReturnValueOnce(first.promise)
      .mockReturnValueOnce(second.promise)
      .mockReturnValueOnce(deferred<ChatReply>().promise);
    const { result } = renderHook(() => useChat("en"));

    act(() => result.current.send("First"));
    await act(async () => first.resolve(reply("abc")));
    act(() => result.current.send("Second"));
    await act(async () => second.reject(new Error("502")));

    act(() => result.current.retry());

    expect(result.current.status).toBe("sending");
    expect(result.current.messages).toHaveLength(3);
    expect(sendChatMock).toHaveBeenLastCalledWith({
      message: "Second",
      session_id: "abc",
      lang: "en",
    });
  });

  it("after a successful retry, the next question uses the session id of the retry's answer", async () => {
    const first = deferred<ChatReply>();
    const second = deferred<ChatReply>();
    sendChatMock
      .mockReturnValueOnce(first.promise)
      .mockReturnValueOnce(second.promise)
      .mockReturnValueOnce(deferred<ChatReply>().promise);
    const { result } = renderHook(() => useChat("en"));

    act(() => result.current.send("First"));
    await act(async () => first.reject(new Error("502")));
    act(() => result.current.retry());
    await act(async () => second.resolve(reply("abc")));

    expect(result.current.status).toBe("idle");

    act(() => result.current.send("Follow-up"));
    expect(sendChatMock).toHaveBeenLastCalledWith({
      message: "Follow-up",
      session_id: "abc",
      lang: "en",
    });
  });

  it("when the first question fails, the retry is sent without a session id", async () => {
    const first = deferred<ChatReply>();
    sendChatMock
      .mockReturnValueOnce(first.promise)
      .mockReturnValueOnce(deferred<ChatReply>().promise);
    const { result } = renderHook(() => useChat("en"));

    act(() => result.current.send("First"));
    await act(async () => first.reject(new Error("502")));
    act(() => result.current.retry());

    expect(sendChatMock).toHaveBeenLastCalledWith({
      message: "First",
      session_id: null,
      lang: "en",
    });
  });

  it("a language chosen after the error is used by the retry, and the session is kept", async () => {
    const first = deferred<ChatReply>();
    const second = deferred<ChatReply>();
    sendChatMock
      .mockReturnValueOnce(first.promise)
      .mockReturnValueOnce(second.promise)
      .mockReturnValueOnce(deferred<ChatReply>().promise);
    const { result, rerender } = renderHook(({ lang }) => useChat(lang), {
      initialProps: { lang: "en" as Language },
    });

    act(() => result.current.send("First"));
    await act(async () => first.resolve(reply("abc")));
    act(() => result.current.send("Second"));
    await act(async () => second.reject(new Error("502")));
    rerender({ lang: "de" });
    act(() => result.current.retry());

    expect(sendChatMock).toHaveBeenLastCalledWith({
      message: "Second",
      session_id: "abc",
      lang: "de",
    });
  });

  it("two quick retries send only one request", async () => {
    const first = deferred<ChatReply>();
    sendChatMock
      .mockReturnValueOnce(first.promise)
      .mockReturnValue(deferred<ChatReply>().promise);
    const { result } = renderHook(() => useChat("en"));

    act(() => result.current.send("First"));
    await act(async () => first.reject(new Error("502")));
    act(() => {
      result.current.retry();
      result.current.retry();
    });

    expect(sendChatMock).toHaveBeenCalledTimes(2);
  });
});

describe("useChat reset (FE-4)", () => {
  it("idle -> idle: clears the messages and the next question is sent without a session id", async () => {
    const first = deferred<ChatReply>();
    sendChatMock
      .mockReturnValueOnce(first.promise)
      .mockReturnValueOnce(deferred<ChatReply>().promise);
    const { result } = renderHook(() => useChat("en"));

    act(() => result.current.send("First"));
    await act(async () => first.resolve(reply("abc")));
    act(() => result.current.reset());

    expect(result.current.status).toBe("idle");
    expect(result.current.messages).toEqual([]);

    act(() => result.current.send("Second"));
    expect(sendChatMock).toHaveBeenLastCalledWith({
      message: "Second",
      session_id: null,
      lang: "en",
    });
  });

  it("failed -> idle: removes the error", async () => {
    const first = deferred<ChatReply>();
    sendChatMock.mockReturnValueOnce(first.promise);
    const { result } = renderHook(() => useChat("en"));

    act(() => result.current.send("First"));
    await act(async () => first.reject(new Error("502")));
    act(() => result.current.reset());

    expect(result.current.status).toBe("idle");
    expect(result.current.messages).toEqual([]);
  });

  it("sending -> idle: a new question can be sent at once, and the late answer is ignored", async () => {
    const first = deferred<ChatReply>();
    sendChatMock
      .mockReturnValueOnce(first.promise)
      .mockReturnValue(deferred<ChatReply>().promise);
    const { result } = renderHook(() => useChat("en"));

    act(() => result.current.send("First"));
    act(() => result.current.reset());

    expect(result.current.status).toBe("idle");
    expect(result.current.messages).toEqual([]);

    act(() => result.current.send("New"));
    expect(sendChatMock).toHaveBeenLastCalledWith({
      message: "New",
      session_id: null,
      lang: "en",
    });

    await act(async () => first.resolve(reply("old")));

    expect(result.current.status).toBe("sending");
    expect(result.current.messages).toHaveLength(1);

    // The new question is still open, so a second send is blocked.
    act(() => result.current.send("Again"));
    expect(sendChatMock).toHaveBeenCalledTimes(2);
  });

  it("a request that fails after the reset shows no error", async () => {
    const first = deferred<ChatReply>();
    sendChatMock.mockReturnValueOnce(first.promise);
    const { result } = renderHook(() => useChat("en"));

    act(() => result.current.send("First"));
    act(() => result.current.reset());
    await act(async () => first.reject(new Error("502")));

    expect(result.current.status).toBe("idle");
    expect(result.current.messages).toEqual([]);
  });
});
