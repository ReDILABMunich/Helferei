import type { en } from "./en";

export const de: typeof en = {
  code: "de",
  name: "Deutsch",
  short: "DE",
  languageLabel: "Sprache",
  welcome: `Willkommen! Ich bin ATLAS, Ihr KI-Assistent für den deutschen Fragebogen zur steuerlichen Erfassung für Einzelunternehmen.\\
Ich helfe Ihnen dabei, das Formular zu verstehen, erkläre Ihnen die Bedeutung der einzelnen Felder, welche Informationen Sie benötigen, und begleite Sie Schritt für Schritt durch die 23 Abschnitte. Sie können Ihre Fragen auf Deutsch oder Englisch stellen.

**Für eine optimale Nutzung:**

- Halten Sie Ihren ELSTER-Fragebogen in einem anderen Fenster geöffnet.
- Nutzen Sie ATLAS parallel zu ELSTER und tragen Sie die Informationen selbst ein.
- ATLAS kann das ELSTER-Formular nicht für Sie ausfüllen oder übermitteln.
- Ihr Chatverlauf wird nicht gespeichert.

**Wie kann ich Ihnen helfen?**`,
  hint: "Navigieren Sie nach Abschnittsnummer oder deutschem Feldnamen, oder stellen Sie eine beliebige Frage. z. B. „Abschnitt 7“, „Geburtsdatum“, „Was ist eine IBAN?“",
  toggleHint: "Tipps ein- oder ausblenden",
  title: "ATLAS",
  subtitle: "KI-Assistent für den Fragebogen zur steuerlichen Erfassung für Einzelunternehmen",
  inputPlaceholder: "Geben Sie hier Ihre Frage ein …",
  disclaimer:
    "ATLAS ist eine KI und kann Fehler machen. Bitte überprüfen Sie wichtige Angaben, bevor Sie Ihre steuerlichen Angaben übermitteln.",
  send: "Senden",
  tooLong: "Ihre Nachricht ist zu lang. Bitte halten Sie sie unter 800 Zeichen.",
  thinking: "Denkt nach",
  error: {
    title: "Etwas ist schiefgelaufen.",
    body: "Ich konnte Ihre Anfrage nicht verarbeiten.\nBitte versuchen Sie es erneut.",
    retry: "Erneut versuchen",
  },
  newChat: {
    button: "Neuer Chat",
    title: "Möchten Sie wirklich eine neue Unterhaltung beginnen?",
    body: "Dadurch wird Ihre aktuelle Unterhaltung gelöscht.",
    cancel: "Abbrechen",
    confirm: "Ja, zurücksetzen",
    close: "Schließen",
  },
};
