const BASE_URL = import.meta.env.DEV ? "/api" : "https://helferei.onrender.com";

export async function ping(): Promise<string> {
  const response = await fetch(`${BASE_URL}/`);

  if (!response.ok) {
    throw new Error(`Request failed with status ${response.status}`);
  }

  const data = await response.json();
  return data.message;
}

export async function sendChat(text: string): Promise<string> {
  const response = await fetch(`${BASE_URL}/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ prompt: text }),
  });

  if (!response.ok) {
    throw new Error(`Request failed with status ${response.status}`);
  }

  const data = await response.json();
  return data.answer;
}
