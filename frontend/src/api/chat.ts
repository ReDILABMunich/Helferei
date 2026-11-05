import type { ChatReply, ChatRequest } from "../types";

const BASE_URL = "https://helferei.onrender.com";

export async function sendChat(request: ChatRequest): Promise<ChatReply> {
  const response = await fetch(`${BASE_URL}/chat`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-API-Key": import.meta.env.VITE_API_KEY,
    },
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    throw new Error(`Request failed with status ${response.status}`);
  }

  return response.json();
}
