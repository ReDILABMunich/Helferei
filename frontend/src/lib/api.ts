const BASE_URL = "/api";

export async function ping(): Promise<string> {
  const response = await fetch(`${BASE_URL}/`);

  if (!response.ok) {
    throw new Error(`Request failed with status ${response.status}`);
  }

  const data = await response.json();
  return data.message;
}
