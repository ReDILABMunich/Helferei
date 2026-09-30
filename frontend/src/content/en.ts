// Arayüzdeki her metin burada. Hiçbir .tsx dosyasında kullanıcıya görünen
// düz metin bırakma; Almanca turu geldiğinde tek yapılacak iş de.ts yazmak olsun.

export const CHAR_LIMIT = 800;

export const WELCOME_MESSAGE = `Welcome! I'm ATLAS, your AI assistant for the German tax registration form
"Fragebogen zur steuerlichen Erfassung für Einzelunternehmen."
I can help you understand the form, explain what each field means, what information you need, and guide you through its 23 sections step by step. You can ask questions in English or German

**For the best experience:**

- Keep your ELSTER tax form open in another window.
- Use ATLAS alongside ELSTER and enter the information yourself.
- ATLAS cannot fill out or submit the ELSTER form for you.
- Your chat history won't be saved.

**How can I help you?**`;

export const en = {
  appName: "ATLAS",
  tagline: "AI assistant for the German self-employment tax registration form",
  language: { en: "EN", de: "DE", english: "English", german: "Deutsch" },
  newChat: "New Chat",
  hint: 'Navigate by section number, German field name, or ask any question. e.g. "Section 7", "Geburtsdatum", "what is IBAN?"',
  inputPlaceholder: "Enter your question here...",
  charLimitError: "Your message is too long. Please keep it under 800 characters",
  thinking: "Thinking",
  error: {
    title: "Something went wrong.",
    body: "I couldn't process your request. Please try again.",
    retry: "Try again",
  },
  dialog: {
    title: "Are you sure you want to start a new conversation?",
    body: "This will clear your current conversation.",
    cancel: "Cancel",
    confirm: "Yes, Reset",
  },
  disclaimer:
    "ATLAS is an AI and may make mistakes. Please verify important information before submitting your tax registration.",
  a11y: {
    send: "Send message",
    newChat: "Start a new conversation",
    openMenu: "Open menu",
    closeMenu: "Close menu",
    closeDialog: "Close dialog",
    expandHint: "Show the hint",
    collapseHint: "Hide the hint",
    switchToGerman: "Switch to German (not available yet)",
  },
};
