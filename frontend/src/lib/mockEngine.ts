// Mock engine: a fake stand-in for the real chat API.
// It has the same shape we proposed to the backend (POST /chat), so when the
// real endpoint is ready the UI only has to swap this function for a fetch call.
// The canned replies imitate the real agent: every answer starts with a
// position line (the 📍 the engine puts on top of each reply).

export type Language = 'en' | 'de'

export type ChatRequest = {
  message: string
  language: Language
}

export type ChatResponse = {
  reply: string
}

// How long the mock pretends to think, so the loading state is visible.
const DELAY_MS = 700

// Send a message containing this word to make the mock fail on purpose,
// so the error state can be tested without breaking anything.
const FAIL_WORD = 'fail'

const texts = {
  en: {
    empty: '📍 Section 1 - Tax office and personal details\n\nI did not get a question. Type where you are in the form, or a section number from 1 to 23.',
    greeting: '📍 Section 1 - Tax office and personal details\n\nHello. I explain the German tax registration form (Fragebogen zur steuerlichen Erfassung). Tell me which field you are on, or send a section number from 1 to 23.',
    section: (n: number) =>
      `📍 Section ${n}\n\nWe are now in section ${n}. This is a mock reply, so the real explanation is not here yet. In the real engine this text comes from the form JSON, in the language you selected.`,
    next: '📍 Section 2 - Details of the business\n\nMoving to the next part of the form. This is a mock reply.',
    fallback: (message: string) =>
      `📍 Section 1 - Tax office and personal details\n\nYou asked: "${message}". This is a mock reply, the real engine is not connected yet. When the backend is ready this text comes from the form JSON.`,
    error: 'Mock engine failed on purpose',
  },
  de: {
    empty: '📍 Abschnitt 1 - Finanzamt und persönliche Angaben\n\nIch habe keine Frage bekommen. Schreibe, wo du im Formular bist, oder eine Abschnittsnummer von 1 bis 23.',
    greeting: '📍 Abschnitt 1 - Finanzamt und persönliche Angaben\n\nHallo. Ich erkläre den Fragebogen zur steuerlichen Erfassung. Sag mir, in welchem Feld du bist, oder schicke eine Abschnittsnummer von 1 bis 23.',
    section: (n: number) =>
      `📍 Abschnitt ${n}\n\nWir sind jetzt in Abschnitt ${n}. Das ist eine Test-Antwort, die echte Erklärung fehlt noch. Im echten System kommt dieser Text aus dem Formular-JSON, in der gewählten Sprache.`,
    next: '📍 Abschnitt 2 - Angaben zum Betrieb\n\nWir gehen zum nächsten Teil des Formulars. Das ist eine Test-Antwort.',
    fallback: (message: string) =>
      `📍 Abschnitt 1 - Finanzamt und persönliche Angaben\n\nDu hast gefragt: "${message}". Das ist eine Test-Antwort, das echte System ist noch nicht angeschlossen. Sobald das Backend fertig ist, kommt dieser Text aus dem Formular-JSON.`,
    error: 'Mock-Engine ist absichtlich fehlgeschlagen',
  },
}

function pickReply({ message, language }: ChatRequest): string {
  const t = texts[language]
  const clean = message.trim()
  const lower = clean.toLowerCase()

  if (clean === '') return t.empty
  if (['hi', 'hello', 'hey', 'hallo', 'guten tag'].includes(lower)) return t.greeting
  if (['next', 'weiter'].includes(lower)) return t.next

  // A bare number means "go to that section", the same as in the real engine.
  if (/^\d+$/.test(clean)) {
    const section = Number(clean)
    if (section >= 1 && section <= 23) return t.section(section)
  }

  return t.fallback(clean)
}

/**
 * Fake version of POST /chat. Waits a moment, then returns a canned reply.
 * Rejects with an Error when the message contains the word "fail", so the UI
 * can show its error state.
 */
export function sendMessage(request: ChatRequest): Promise<ChatResponse> {
  return new Promise((resolve, reject) => {
    setTimeout(() => {
      if (request.message.toLowerCase().includes(FAIL_WORD)) {
        reject(new Error(texts[request.language].error))
        return
      }
      resolve({ reply: pickReply(request) })
    }, DELAY_MS)
  })
}
