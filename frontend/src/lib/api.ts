const BASE_URL = import.meta.env.DEV ? "/api" : "https://helferei.onrender.com";

export type ChatReply = {
  answer: string;
  responseId: string;
};

export async function sendChat(
  text: string,
  previousResponseId: string | null,
): Promise<ChatReply> {
  const response = await fetch(`${BASE_URL}/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      message: text,
      previous_response_id: previousResponseId,
    }),
  });

  if (!response.ok) {
    throw new Error(`Request failed with status ${response.status}`);
  }

  const data = await response.json();
  return { answer: data.answer, responseId: data.response_id };
}
