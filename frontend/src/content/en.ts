import type { Language } from "../types";

export const en = {
  code: "en" as Language,
  name: "English",
  short: "EN",
  languageLabel: "Language",
  welcome: `Welcome! I'm ATLAS, your AI assistant for the German tax registration form\\
"Fragebogen zur steuerlichen Erfassung für Einzelunternehmen."\\
I can help you understand the form, explain what each field means, what information you need, and guide you through its 23 sections step by step. You can ask questions in English or German

**For the best experience:**

- Keep your ELSTER tax form open in another window.
- Use ATLAS alongside ELSTER and enter the information yourself.
- ATLAS cannot fill out or submit the ELSTER form for you.
- Your chat history won't be saved.

**How can I help you?**`,
  hint: "Navigate by section number, German field name, or ask any question. e.g. “Section 7”, “Geburtsdatum”, “what is IBAN?”",
  toggleHint: "Show or hide tips",
  title: "ATLAS",
  subtitle: "AI assistant for the German self-employment tax registration form",
  inputPlaceholder: "Enter your question here...",
  disclaimer:
    "ATLAS is an AI and may make mistakes. Please verify important information before submitting your tax registration.",
  send: "Send",
  thinking: "Thinking",
  error: {
    title: "Something went wrong.",
    body: "I couldn't process your request.\nPlease try again.",
  },
};
