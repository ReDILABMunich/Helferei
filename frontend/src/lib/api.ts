const BASE_URL = "https://helferei.onrender.com";

// Backend kontratı:
//   istek  -> { message, session_id }   ilk turda session_id null
//   cevap  -> { answer, session_id, breadcrumb }
// Çok turlu konuşmayı ayakta tutan şey session_id; geri göndermezsen
// backend her mesajı yeni bir konuşma sayar.
export type ChatReply = {
  answer: string;
  sessionId: string;
  breadcrumb: string | null;
};

export async function sendChat(
  text: string,
  sessionId: string | null,
): Promise<ChatReply> {
  const response = await fetch(`${BASE_URL}/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      message: text,
      session_id: sessionId,
    }),
  });

  if (!response.ok) {
    throw new Error(`Request failed with status ${response.status}`);
  }

  const data = await response.json();
  return {
    answer: data.answer,
    sessionId: data.session_id,
    breadcrumb: data.breadcrumb ?? null,
  };
}
