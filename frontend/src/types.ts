export type Language = "en" | "de";

// The shape of POST /chat on the backend. Field names follow the backend.
export type ChatRequest = {
  message: string;
  session_id: string | null;
  lang: Language;
};

export type ChatReply = {
  answer: string;
  session_id: string;
  breadcrumb: string;
};

export type ConversationStatus = "idle" | "sending" | "failed";

export type Message = {
  id: number;
  role: "user" | "bot";
  text: string;
  breadcrumb: string | null;
};
