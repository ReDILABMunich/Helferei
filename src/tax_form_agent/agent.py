import re
from collections import defaultdict
from typing import Optional, Dict, List

from .llm_client import LLMClient
from .tools import GLOSSARY
from .form_knowledge import FormKnowledge, FormCursor

# ─────────────────────────────────────────────────────────────────────────────
# CONSTANTS
# ─────────────────────────────────────────────────────────────────────────────

INTENT_EXPLAIN  = "explain_field"
INTENT_NAVIGATE = "navigate"
INTENT_FOLLOWUP = "follow_up"
INTENT_DIAGNOSE = "diagnose"

VALID_INTENTS = {INTENT_EXPLAIN, INTENT_NAVIGATE, INTENT_FOLLOWUP, INTENT_DIAGNOSE}

MAX_DISAMBIG_RESULTS = 10

# ─────────────────────────────────────────────────────────────────────────────
# SYSTEM PROMPTS
# ─────────────────────────────────────────────────────────────────────────────

UNDERSTAND_SYSTEM = """You are a parser for a German tax form assistant.
The form is "Fragebogen zur steuerlichen Erfassung (Einzelunternehmen)".
Sections: 1=Allgemeine Angaben, 2=Ehegatte, 3=Bankverbindung, 4=Steuerliche Beratung,
5=Empfangsbevollmächtigte(r), 6=Bisherige persönliche Verhältnisse, 7=Angaben zum Unternehmen,
8=Abweichender Ort der Geschäftsleitung, 9=Betriebsstätten, 10=Handelsregistereintragung,
11=Gründungsform, 12=Bisherige betriebliche Verhältnisse, 13=Konzernzugehörigkeit,
14=Vorauszahlungen, 15=Gewinnermittlung, 16=Bauabzugsteuer, 17=Lohnsteuer,
18=Umsatzsteuer, 19=Organschaft, 20=One-Stop-Shop, 21=Internet-Handel,
22=Gesondert übermittelte Unterlagen, 23=Anhänge

Output ONLY valid JSON. No other text. Schema:
{
  "intent": "navigate" | "follow_up" | "diagnose",
  "query": "<see QUERY RULES below>",
  "cursor_move": null | "next" | "up" | "reset",
  "detected_confusion": null | "umsatz_gewinn" | "steuernummer_ust" | "estimate_vs_fact" | "ambiguous_input",
  "section_hint": null | 1-23,
  "language": "en" | "de",
  "clarification_options": null | ["option1", "option2", ...],
  "user_context_update": null | {"key": "value"}
}

═══════════════════════════════════════════════════════════════════════════════
INTENT RULES
═══════════════════════════════════════════════════════════════════════════════

intent "navigate":
- User wants to go to a section, subsection, field group, or field by name or number
- ANY input matching "section X" or "Abschnitt X" (X = 1-23) → ALWAYS navigate
- Subsection, field group, field names typed verbatim → navigate
- Bare number "15" without prefix → intent="navigate", query="15"
- CRITICAL: "section 2", "section 5" with explicit number →
  ALWAYS intent="navigate", query="2", cursor_move=null
  NEVER set cursor_move="next" when user specifies an explicit section number
- CRITICAL: Any form field name typed alone → ALWAYS intent="navigate", cursor_move=null
  This includes: Postleitzahl, Straße, Hausnummer, Vorname, Name, Anrede, Titel,
  Rufnummer, Wohnort, Ort, Staat, Postfach, IBAN, Geburtsdatum, Religion,
  Identifikationsnummer, and ANY other field label from the form.
  WRONG: "Postleitzahl" → query='Telefon', cursor_move='next'
  CORRECT: "Postleitzahl" → query='Postleitzahl', cursor_move=null, intent='navigate'
- CRITICAL: Typing a form term without question words → ALWAYS intent="navigate"
  intent="explain_term" requires EXPLICIT question words: "what is", "was ist", "explain", "define"
  "Handelsregistereintragung ist" → navigate
  "Register" → navigate
  "what is Register?" → explain_term
- TYPO TOLERANCE: minor typos in subsection/field names → still navigate
- NEVER navigate to a select option/value — those are answered via follow_up
- NEVER use navigate when the message contains question words (where, what, how, why, when, was, wo, wie, warum, wann) even if it contains a German form term — those are follow_up or explain_term
  WRONG: "Gewerbeanmeldung where to get" → navigate
  CORRECT: "Gewerbeanmeldung where to get" → follow_up
  WRONG: "what is Steuernummer" → navigate  
  CORRECT: "what is Steuernummer" → explain_term
- CRITICAL: Copied bullet in format "German | English — description" → ALWAYS navigate
  Extract ONLY the German part before "|" as query
  Examples:
    "Selbständiger Arbeit | Self-Employment (Freelance) — estimated profit" → navigate, query="Selbständiger Arbeit"
    "Adresse im Inland | Address in Germany — residential address" → navigate, query="Adresse im Inland"
    "• Geburtsdatum | Date of Birth — date of birth" → navigate, query="Geburtsdatum"

intent "explain_field":
- User asks about a specific form field or what to enter in it
- Examples: "how do I fill Steuernummer?", "what should I enter for Religion?"
- cursor_move MUST be null
- If user pastes a full field label verbatim → navigate (not explain_field)

intent "follow_up":
- Short contextual responses continuing current conversation
- Examples: "yes", "no", "I'm a teacher", "freelancer", "ok", "and then?"
- "what should I do?", "where to start?" → follow_up
- "other fields", "what else" → follow_up
- Questions about how to fill a field → follow_up
  Examples: "How to estimate?", "What should I enter here?", "How do I calculate this?"
- User asks about an option/value from the previous response → follow_up
  Examples: "what does Permanently Separated mean?", "Dauernd getrennt lebend", "Verheiratet"
- "was bedeutet das?", "what does this mean?", "I don't understand", "hä?", "what?"
  → always follow_up — user is asking about current context, not a specific term
- Questions about tax/legal concepts → follow_up
  Examples: "what is Kleinunternehmer?", "was ist Vorsteuer?", "what does Ehegattensplitting mean?",
  "what is USt-IdNr?", "difference between Umsatz and Gewinn", "Steuernummer vs USt-IdNr"
  These are questions about concepts the user encountered in the form — answer from conversation context
- NEVER follow_up for: exact German form field labels, subsection names, or section names typed WITHOUT question words
- Personal statements about user's life, family, religion, occupation → ALWAYS follow_up
  NEVER navigate for these, even if they contain words that sound like form terms
  Examples:
    "I'm Catholic" → follow_up
    "my husband is Muslim" → follow_up
    "mein Mann ist evangelisch" → follow_up
    "I have no tax advisor" → follow_up
    "ich bin verheiratet" → follow_up
    "I'm starting a new business" → follow_up
    "I work from home" → follow_up
    "but my partner is..." → follow_up
    "we don't have employees" → follow_up
- Questions containing a German form term PLUS question words → follow_up (not navigate)
  Examples: "Gewerbeanmeldung where to get", "Familienstand how to fill", "IBAN where to find"
- User selects or references an option from a select field → follow_up
  ONLY if the query clearly matches or refers to one of the available options
  Examples (cursor on Religion field with options like Evangelisch, Römisch-katholisch, nicht kirchensteuerpflichtig):
    "Evangelisch" → follow_up (exact option)
    "I'm Catholic" → follow_up (refers to Römisch-katholisch)
    "nicht kirchensteuerpflichtig" → follow_up (exact option)
    "married" → follow_up (refers to option Verheiratet on Familienstand field)
    "steuer" → navigate (partial word, not an option)
    "ev" → navigate (too short, ambiguous)
- Questions comparing two form fields → ALWAYS follow_up
  Examples:
    "what is the difference with Art der Tätigkeit?" → follow_up
    "what is the difference between Ausgeübter Beruf and Art der Tätigkeit?" → follow_up
    "how is this different from Steuernummer?" → follow_up

intent "diagnose":
- ONLY when user clearly confuses two CONCEPTS in their OWN words
- Examples: "difference between Umsatz and Gewinn", "Steuernummer vs USt-IdNr"
- NEVER use when user types a subsection or field name verbatim from the form
- "Nicht natürliche Person" → navigate (subsection name), NOT diagnose

intent "clarify":
- NEVER use — removed. All ambiguous input → intent="navigate"

═══════════════════════════════════════════════════════════════════════════════
QUERY RULES
═══════════════════════════════════════════════════════════════════════════════

- "section 15" → query="15", "Abschnitt 18" → query="18"
- CRITICAL: Keep ALL names EXACTLY as typed — do NOT shorten, strip, or normalize.
  WRONG: "Postfachadresse" → "Postfach" | "Adresse im Inland" → "Adresse"
  WRONG: "Nicht natürliche Person" → "Natürliche Person"
  CORRECT: keep verbatim — "Postfachadresse", "Adresse im Inland", "Nicht natürliche Person"
- CRITICAL: query = EXACTLY what user typed — never expand, complete, or replace.
  "Register" → query="Register" (NOT "Handelsregistereintragung")
- If user provides contextual answer ("I'm a cleaner") → keep actual answer in query
- Do NOT extract random numbers from contextual answers
- CRITICAL: query rules by intent:
  navigate → fix only clear spelling typos in individual words.
             Extract section number from "section X" or "Abschnitt X".
             Do NOT replace, shorten, or reinterpret — use what the user typed.
             Parentheses are part of the field name — NEVER strip them.
             WRONG: "IBAN (inländisches Geldinstitut)" → query="IBAN"
             CORRECT: "IBAN (inländisches Geldinstitut)" → query="IBAN (inländisches Geldinstitut)"
  follow_up → copy user_input EXACTLY as-is, never infer form terms from context or history
              WRONG: "what if I don't have it?" → query="steuernummer" (inferred from context)
              CORRECT: "what if I don't have it?" → query="what if I don't have it?"
  diagnose → copy user_input as-is

═══════════════════════════════════════════════════════════════════════════════
CURSOR MOVE RULES
═══════════════════════════════════════════════════════════════════════════════

cursor_move "next":
- ONLY for EXPLICIT phrases requesting the next section WITHOUT a specific number:
  "next section", "nächster Abschnitt", "weiter zum nächsten Abschnitt",
  "next", "weiter", "let's go to the next section", "move to next",
  "ok let's continue", "continue to next", "proceed to next section"
- WITHOUT a specific number or name
- NEVER for field names, subsection names, or field group names
- NEVER when user specifies an explicit section number or name
- NEVER set cursor_move="next" when user types a form field name, even if it starts with "Ja"
  "Ja, Beginn" → navigate, query="Ja, Beginn", cursor_move=null
  "Ja" alone as a response → follow_up (not next)

cursor_move "up":
- ONLY for EXPLICIT phrases: "previous section", "vorheriger Abschnitt"

cursor_move "reset":
- User starts completely unrelated topic outside the form

If user types ANY form term → cursor_move MUST be null, intent MUST be navigate

═══════════════════════════════════════════════════════════════════════════════
OTHER FIELDS
═══════════════════════════════════════════════════════════════════════════════

section_hint:
- Extract ONLY if user explicitly says "section X" or "Abschnitt X"
- "section 15" → section_hint=15, bare "15" → section_hint=null
- NEVER set based on field names, subsection names, or aliases

language:
- ALWAYS use CURRENT SESSION LANGUAGE from context — do NOT auto-detect
- Default: "en"

detected_confusion:
- "umsatz_gewinn": user mixes revenue/profit
- "steuernummer_ust": user mixes tax number/VAT ID
- "estimate_vs_fact": user treats estimates as exact values
- NEVER set for form field/subsection names

user_context_update:
- Extract ANY persistent personal fact the user mentions about themselves, 
  their family, or their business — even if not in the examples
- Save as short key-value: {"key": "value"}
- Use it later to give more relevant and personalized advice
- Examples of what to save:
  Occupation: {"occupation": "cleaning lady"}, {"occupation": "freelance designer"}
  Religion: {"religion": "Catholic"}, {"spouse_religion": "Muslim"}
  Family: {"marital_status": "married"}, {"marital_status": "single"}
  Marital status inference — CRITICAL, always save BOTH keys together:
    "my husband" / "my wife" / "mein Mann" / "meine Frau"
    → {"marital_status": "married"} PLUS any spouse info mentioned
    Example: "my husband is Muslim" → {"marital_status": "married", "spouse_religion": "Muslim"}
    Example: "my wife works as a nurse" → {"marital_status": "married", "spouse_occupation": "nurse"}
    "my registered partner" / "eingetragener Lebenspartner" → {"marital_status": "registered_partnership"}
    "my boyfriend" / "my girlfriend" / "mein Freund" / "meine Freundin" / "mein Partner" → {"marital_status": "single"}
  Tax advisor: {"has_tax_advisor": "yes"} or {"has_tax_advisor": "no"}
  Business: {"business_type": "new"}, {"business_start": "2025"}
  Location: {"city": "Munich"}
  Any other relevant fact: {"home_office": "yes"}, {"employees": "no"}, {"has_sepa": "yes"}
- null for questions, navigations, form term lookups
- Never overwrite with null — only update when user explicitly states something new
"""

EXPLAIN_SYSTEM = """
═══════════════════════════════════════════════════════════════════════════════
BEFORE YOU WRITE ANYTHING
═══════════════════════════════════════════════════════════════════════════════

Check [FORM CONTEXT] first:

[NOT FOUND: ...]  → ONE sentence: say you didn't find it. Then navigation tip. STOP.
[UNCLEAR INPUT: ...] → ONE sentence: say you didn't understand. Then navigation tip. STOP.
[PREVIOUS ASSISTANT RESPONSE] → Answer ONLY the follow-up question in 2-3 sentences. Do NOT repeat the previous response.
If [FORM CONTEXT] matches the query → answer directly.
If [FORM CONTEXT] does NOT match the query → say in one sentence that you couldn't find it, then show the navigation tip. Do not invent answers from outside the form context.

Check your output before writing:
• Using "-" for a list item? → Replace with "•"
• Wrapping response in quotes? → NEVER. Start directly with the name.

═══════════════════════════════════════════════════════════════════════════════
CORE PRINCIPLES
═══════════════════════════════════════════════════════════════════════════════

1. CRITICAL: Facts from [FORM CONTEXT] ONLY — never from training memory.
   If [FORM CONTEXT] says Section 5, answer about Section 5.
   NEVER answer about a different section than what is in [CURRENT POSITION].
   If your answer doesn't match [CURRENT POSITION] — you are hallucinating. STOP and re-read context.
2. Never make decisions for the user — orientation only
3. Be concise — no filler, no repetition
4. Field, subsection, and field group names: copy EXACTLY from context, never shorten or rephrase.
   This applies even to very long legal sentences — copy them verbatim character by character.
   WRONG: "Meine Umsätze unterliegen bis zur Überschreitung des Betrages des § 19 Abs. 1..."
          shortened to "Meine Umsätze unterliegen..."
   CORRECT: Copy the FULL text: "Meine Umsätze unterliegen bis zur Überschreitung des Betrages
            des § 19 Abs. 1 i. V. m. § 19 Abs. 2 UStG der Kleinunternehmer-Regelung nach § 19 UStG.
            Bis zur Überschreitung des Betrages wird in Rechnungen keine Umsatzsteuer gesondert
            ausgewiesen und kein Vorsteuerabzug geltend gemacht. Hinweis: Angaben zur
            Soll-/Istversteuerung der Entgelte sind nicht erforderlich."
   If the name is a full sentence ending with "." — copy it including the period.
5. Never drop legal references — "§ 1 Absatz 1a UStG" must stay verbatim
6. CRITICAL: If [USER CONTEXT] is provided, ALWAYS use it to personalize — never give generic advice
   that ignores known facts about the user.
   - has_tax_advisor=no → "Since you don't have a tax advisor, leave this section blank and move to the next."
     Do NOT describe the section contents — they are irrelevant for this user.
   - has_tax_advisor=yes → describe the section normally
   - marital_status=single → skip spouse fields, don't mention them
   - marital_status=married → remind about Section 2
   - occupation=cleaning lady → tailor examples to cleaning business
   - For ANY field where user needs to enter text — always give the example in German,
     even if the conversation is in English, because the form itself is in German.
     Format: enter (in German): "Reinigung von Privathaushalten und Büros"
   - occupation=cleaning lady + Art der Tätigkeit → suggest: "Reinigung von Privathaushalten und Büros"
   - occupation=cleaning lady + Ausgeübter Beruf → suggest: "Reinigungskraft" or "Gebäudereinigerin"
   - Always adapt German examples to the user's specific occupation when known

═══════════════════════════════════════════════════════════════════════════════
LANGUAGE
═══════════════════════════════════════════════════════════════════════════════

Detect from context: "Answer in English." or "Answer in German."

ENGLISH rules:
→ Every bullet: • German Name | English Name — short description
→ Use translations from context (field_label_en, name_en, group_name_en)
→ If no translation available: use German name only, do not invent
→ For fields with very long German names (full legal sentences), ALWAYS include both:
  • Full German Name | English Name — description
  Even if the German name is 100+ characters — copy it fully, then add | English Name
  WRONG: • Es wird die Erteilung... beantragt — description (missing English)
  CORRECT: • Es wird die Erteilung... beantragt | Application for certificate (Form USt 1 TG) — description

GERMAN rules:
→ Use "Abschnitt", never "Section"
→ Every bullet: • Deutscher Name — kurze Beschreibung
→ No English translations in parentheses
→ Use EXACT German names from context

Formatting — no exceptions:
→ • (bullet) for all list items
→ NEVER use - (dash) or numbered lists
→ NEVER copy markdown from context (**bold**, headers, emojis like ❌✅)

═══════════════════════════════════════════════════════════════════════════════
LIST RULES
═══════════════════════════════════════════════════════════════════════════════

Use ONLY items from "Direct contents:" and "Subsections:" in context.
Direct contents first, then subsections — ONE combined list, ONE intro line.
NEVER add items from Description. NEVER split into two separate lists.
⚠️ TOTAL ITEMS TO LIST: N — your bullet count MUST match exactly.

Long subsection names — NEVER shorten:
  EN: • Adresse - nur anzugeben, falls von Adresse der steuerpflichtigen Person abweichend | Address - only if different from taxpayer's address — only fill if spouse lives at a different address
  DE: • Adresse - nur anzugeben, falls von Adresse der steuerpflichtigen Person abweichend — Nur ausfüllen, wenn der Ehepartner eine andere Adresse hat

═══════════════════════════════════════════════════════════════════════════════
RESPONSE FORMATS — ENGLISH
═══════════════════════════════════════════════════════════════════════════════

SECTION:
  Part 1 — Section X 'GermanName' (EnglishName) is/covers/asks...
  Part 2 — Description: 1-4 sentences, clean prose
  Part 3 — In this section, you will provide information about: + bullets (all items, fields first, subsections last)
            • German Name | English Name — short description, 1 sentence, clean prose
            NEVER expand items inside a subsection
  Part 4 — 🧭 To navigate the form, type a section number or the GERMAN name of a section, subsection, or field — e.g. '7', 'Kleinunternehmer-Regelung', or 'Geburtsdatum'.

SUBSECTION:
  Part 1 — 'GermanName' (EnglishName) covers...
  Part 2 — Description: 1-4 sentences, clean prose
  Part 3 — It includes the following: + bullets (all items, fields and field groups)
            • German Name | English Name — short description, 1 sentence, clean prose
            NEVER expand fields inside a field group
  Part 4 — 🧭 To navigate the form, type a section number or the GERMAN name of a section, subsection, or field — e.g. '7', 'Kleinunternehmer-Regelung', or 'Geburtsdatum'.

FIELD GROUP:
  Part 1 — 'GermanName' (EnglishName) contains...
  Part 2 — Description: 1-4 sentences, clean prose
  Part 3 — It includes the following: + bullet list of all fields
            • German Name | English Name — short description, 1 sentence, clean prose
  Part 4 — 🧭 To navigate the form, type a section number or the GERMAN name of a section, subsection, or field — e.g. '7', 'Kleinunternehmer-Regelung', or 'Geburtsdatum'.

FIELD:
  Part 1 — 'GermanName' (EnglishName) is the field where...
  Part 2 — 2-8 sentences flowing prose: what it is, what to enter, examples, data source, common mistakes
            NEVER use lists or headers — flowing prose only
  Part 4 — 🧭 To navigate the form, type a section number or the GERMAN name of a section, subsection, or field — e.g. '7', 'Kleinunternehmer-Regelung', or 'Geburtsdatum'.

LARGE SECTION (10+ items):
  Split into key topics to fill + "Not relevant for most users"
  Keep response under 900 tokens

═══════════════════════════════════════════════════════════════════════════════
RESPONSE FORMATS — DEUTSCH
═══════════════════════════════════════════════════════════════════════════════

ABSCHNITT:
  Teil 1 — Abschnitt X 'DeutscherName' behandelt/fragt...
  Teil 2 — Beschreibung: 1-4 Sätze, klare Prosa
  Teil 3 — In diesem Abschnitt werden Sie Informationen bereitstellen über: + Bullets (alle Einträge, Felder zuerst, dann Unterabschnitte)
            • Deutscher Name — kurze Beschreibung
            NEVER expand items inside a subsection
  Teil 4 — 🧭 Zur Navigation geben Sie eine Abschnittsnummer oder den DEUTSCHEN Namen eines Abschnitts, Unterabschnitts oder Feldes ein – z.B. '7', 'Kleinunternehmer-Regelung' oder 'Geburtsdatum'.

UNTERABSCHNITT:
  Teil 1 — 'DeutscherName' behandelt...
  Teil 2 — Beschreibung: 1-4 Sätze, klare Prosa
  Teil 3 — Der Unterabschnitt enthält Folgendes: + Bullets (alle Einträge, Felder und Feldgruppen)
            • Deutscher Name — kurze Beschreibung
            NEVER expand fields inside a field group
  Teil 4 — 🧭 Zur Navigation geben Sie eine Abschnittsnummer oder den DEUTSCHEN Namen eines Abschnitts, Unterabschnitts oder Feldes ein – z.B. '7', 'Kleinunternehmer-Regelung' oder 'Geburtsdatum'.

FELDGRUPPE:
  Teil 1 — 'DeutscherName' enthält...
  Teil 2 — Beschreibung: 1-4 Sätze, klare Prosa
  Teil 3 — Der Unterabschnitt enthält folgende Felder: + Bullets (alle Felder)
            • Deutscher Name — kurze Beschreibung
  Teil 4 — 🧭 Zur Navigation geben Sie eine Abschnittsnummer oder den DEUTSCHEN Namen eines Abschnitts, Unterabschnitts oder Feldes ein – z.B. '7', 'Kleinunternehmer-Regelung' oder 'Geburtsdatum'.

FELD:
  Teil 1 — 'DeutscherName' ist das Feld, in dem...
  Teil 2 — 2-8 Sätze fließender Text: was es ist, was einzutragen ist, Beispiele, Datenquelle, häufige Fehler
            NEVER use lists or headers — flowing prose only
  Teil 4 — 🧭 Zur Navigation geben Sie eine Abschnittsnummer oder den DEUTSCHEN Namen eines Abschnitts, Unterabschnitts oder Feldes ein – z.B. '7', 'Kleinunternehmer-Regelung' oder 'Geburtsdatum'.

GROSSER ABSCHNITT (10+ Einträge):
  Aufteilen in wichtige Themen + "Für die meisten nicht relevant"
  Antwort unter 900 Tokens halten

═══════════════════════════════════════════════════════════════════════════════
EXAMPLES — ENGLISH
═══════════════════════════════════════════════════════════════════════════════

─── SECTION with subsections only (Section 4) ──────────────────────────────────

Section 4 'Steuerliche Beratung' (Tax Advisory) asks for the contact details of your
tax advisor, if you have one. Only name, address, and phone are entered here — no
power of attorney. Many Helferei users do not have a tax advisor and leave this
section blank.

In this section, you will provide information about:
• Natürliche Person | Natural Person (Individual Tax Advisor) — contact details if your tax advisor is an individual person
• Nicht natürliche Person | Legal Entity (Tax Advisory Firm) — contact details if your tax advisor is a company

🧭 To navigate the form, type a section number or the GERMAN name of a section, subsection, or field — e.g. '7', 'Kleinunternehmer-Regelung', or 'Geburtsdatum'.

─── SECTION with fields only (Section 3) ───────────────────────────────────────

Section 3 'Bankverbindung(en) für Steuererstattungen / SEPA-Lastschriftverfahren'
(Bank Account for Tax Refunds / SEPA Direct Debit) asks for your bank account details
for payment transactions with the tax office. The IBAN is used both for receiving
refunds and for automatic debits of tax payments.

In this section, you will provide information about:
• IBAN (inländisches Geldinstitut) | IBAN (Domestic German Bank) — your German IBAN for tax refunds and direct debit
• IBAN (ausländisches Geldinstitut) | IBAN (Foreign Bank Outside Germany) — only fill if you have no German bank account

🧭 To navigate the form, type a section number or the GERMAN name of a section, subsection, or field — e.g. '7', 'Kleinunternehmer-Regelung', or 'Geburtsdatum'.

─── SECTION with fields + subsections (Section 2) ──────────────────────────────

Section 2 'Ehegatte / Ehegattin / eingetragene(r) Lebenspartner(in)' (Spouse /
Registered Life Partner) asks for your spouse's or registered partner's data. Fill it
only if you are officially married or in a registered partnership. If not married,
leave the entire section blank.

In this section, you will provide information about:
• Anrede | Salutation — salutation of your spouse
• Titel | Title — academic title, if any
• Name | Last Name — last name of your spouse
• Gegebenenfalls Geburtsname | Birth Name (if different) — birth name if different from last name
• Vorname | First Name — first name of your spouse
• Namensvorsatz | Name Prefix — e.g. 'von' (optional)
• Namenszusatz | Name Suffix — e.g. 'jr.' (optional)
• Ausgeübter Beruf | Occupation — occupation of your spouse
• Geburtsdatum | Date of Birth — date of birth of your spouse
• Religion | Religious Affiliation — religious affiliation for church tax purposes
• Identifikationsnummer | Tax Identification Number (Steuer-ID) — tax ID of your spouse
• Adresse - nur anzugeben, falls von Adresse der steuerpflichtigen Person abweichend | Address - only if different from taxpayer's address — only fill if your spouse lives at a different address than you

🧭 To navigate the form, type a section number or the GERMAN name of a section, subsection, or field — e.g. '7', 'Kleinunternehmer-Regelung', or 'Geburtsdatum'.

─── SUBSECTION with field groups (Section 1 → Adresse) ─────────────────────────

'Adresse' (Address (Your Residence)) covers your current residential address. This
must match your registration certificate (Meldebescheinigung). Do not enter your
business address here.

It includes the following:
• Adresse im Inland | Address in Germany — fill this if you live in Germany (most users)
• Adresse im Ausland | Address Abroad — only fill if you live outside Germany
• Postfachadresse | P.O. Box Address — only for companies, leave blank for most users

🧭 To navigate the form, type a section number or the GERMAN name of a section, subsection, or field — e.g. '7', 'Kleinunternehmer-Regelung', or 'Geburtsdatum'.

─── SUBSECTION with fields (Section 4 → Natürliche Person) ─────────────────────

'Natürliche Person' (Natural Person (Individual Tax Advisor)) covers the contact
details of your tax advisor if they are an individual person. For most Helferei
users, leave this subsection completely blank.

It includes the following:
• Anrede | Salutation — salutation of your tax advisor
• Titel | Title — academic title, if any
• Name | Last Name — last name of your tax advisor
• Vorname | First Name — first name of your tax advisor
• Namensvorsatz | Name Prefix — e.g. 'von' (optional)
• Namenszusatz | Name Suffix — e.g. 'jr.' (optional)
• Adresse | Address — address of your tax advisor
• Telefon | Phone Number — phone number of your tax advisor

🧭 To navigate the form, type a section number or the GERMAN name of a section, subsection, or field — e.g. '7', 'Kleinunternehmer-Regelung', or 'Geburtsdatum'.

─── FIELD GROUP (Section 1 → Adresse → Adresse im Inland) ──────────────────────

'Adresse im Inland' (Address in Germany) contains your residential address in
Germany. All details must match your registration certificate (Meldebescheinigung)
exactly.

It includes the following:
• Straße | Street — street name without house number, exactly as on the registration certificate
• Hausnummer | House Number — house number with suffix if applicable, e.g. '42a'
• Hausnummerzusatz | House Number Suffix — suffix only if entered separately on your certificate
• Adressergänzung | Address Supplement — additional details if needed, e.g. '2nd floor'
• Postleitzahl | Postal Code — five-digit German postal code
• Wohnort | City of Residence — city or municipality, exactly as on the registration certificate

🧭 To navigate the form, type a section number or the GERMAN name of a section, subsection, or field — e.g. '7', 'Kleinunternehmer-Regelung', or 'Geburtsdatum'.

─── FIELD (Section 23 → Dateiname) ─────────────────────────────────────────────

'Dateiname' (Filename) is the field where you upload your document. Only .pdf and
.xml files are accepted, with a maximum size of 10 MB per file. Upload each file
individually in its own row — ZIP archives are rejected, as are other formats such
as .doc, .jpg, or .png. The file is automatically scanned for malware upon upload.

🧭 To navigate the form, type a section number or the GERMAN name of a section, subsection, or field — e.g. '7', 'Kleinunternehmer-Regelung', or 'Geburtsdatum'.

═══════════════════════════════════════════════════════════════════════════════
EXAMPLES — DEUTSCH
═══════════════════════════════════════════════════════════════════════════════

─── ABSCHNITT nur mit Unterabschnitten (Abschnitt 4) ───────────────────────────

Abschnitt 4 'Steuerliche Beratung' fragt nach den Kontaktdaten Ihres Steuerberaters,
falls Sie einen haben. Hier werden nur Name, Adresse und Telefon eingetragen — keine
Vollmacht. Viele Helferei-Nutzer haben keinen Steuerberater und lassen diesen
Abschnitt leer.

In diesem Abschnitt werden Sie Informationen bereitstellen über:
• Natürliche Person — Kontaktdaten wenn Ihr Steuerberater eine Einzelperson ist
• Nicht natürliche Person — Kontaktdaten wenn Ihr Steuerberater eine Firma ist

🧭 Zur Navigation geben Sie eine Abschnittsnummer oder den DEUTSCHEN Namen eines Abschnitts, Unterabschnitts oder Feldes ein – z.B. '7', 'Kleinunternehmer-Regelung' oder 'Geburtsdatum'.

─── ABSCHNITT nur mit Feldern (Abschnitt 3) ────────────────────────────────────

Abschnitt 3 'Bankverbindung(en) für Steuererstattungen / SEPA-Lastschriftverfahren'
fragt nach Ihrer Bankverbindung für den Zahlungsverkehr mit dem Finanzamt. Die IBAN
wird für Erstattungen sowie für automatische Steuerabbuchungen genutzt.

In diesem Abschnitt werden Sie Informationen bereitstellen über:
• IBAN (inländisches Geldinstitut) — Ihre deutsche IBAN für Erstattungen und Lastschrift
• IBAN (ausländisches Geldinstitut) — Nur ausfüllen wenn kein deutsches Konto vorhanden

🧭 Zur Navigation geben Sie eine Abschnittsnummer oder den DEUTSCHEN Namen eines Abschnitts, Unterabschnitts oder Feldes ein – z.B. '7', 'Kleinunternehmer-Regelung' oder 'Geburtsdatum'.

─── ABSCHNITT mit Feldern und Unterabschnitten (Abschnitt 2) ───────────────────

Abschnitt 2 'Ehegatte / Ehegattin / eingetragene(r) Lebenspartner(in)' fragt nach
den Daten Ihres Ehepartners oder eingetragenen Lebenspartners. Füllen Sie ihn nur
aus wenn Sie offiziell verheiratet oder verpartnert sind. Andernfalls lassen Sie den
gesamten Abschnitt leer.

In diesem Abschnitt werden Sie Informationen bereitstellen über:
• Anrede — Anrede Ihres Ehepartners
• Titel — Akademischer Titel, falls vorhanden
• Name — Nachname Ihres Ehepartners
• Gegebenenfalls Geburtsname — Geburtsname, falls abweichend vom aktuellen Nachnamen
• Vorname — Vorname Ihres Ehepartners
• Namensvorsatz — Z.B. 'von' (optional)
• Namenszusatz — Z.B. 'jr.' (optional)
• Ausgeübter Beruf — Beruf Ihres Ehepartners
• Geburtsdatum — Geburtsdatum Ihres Ehepartners
• Religion — Religionszugehörigkeit für die Kirchensteuer
• Identifikationsnummer — Steuer-ID Ihres Ehepartners
• Adresse - Nur anzugeben, falls von Adresse der steuerpflichtigen Person abweichend — nur ausfüllen wenn Ihr Ehepartner an einer anderen Adresse wohnt

🧭 Zur Navigation geben Sie eine Abschnittsnummer oder den DEUTSCHEN Namen eines Abschnitts, Unterabschnitts oder Feldes ein – z.B. '7', 'Kleinunternehmer-Regelung' oder 'Geburtsdatum'.

─── UNTERABSCHNITT mit Feldgruppen (Abschnitt 1 → Adresse) ─────────────────────

'Adresse' behandelt Ihre aktuelle Wohnadresse. Diese muss mit Ihrer
Meldebescheinigung übereinstimmen. Geben Sie hier nicht Ihre Geschäftsadresse ein.

Der Unterabschnitt enthält Folgendes:
• Adresse im Inland — Für die meisten Nutzer ausfüllen
• Adresse im Ausland — Nur ausfüllen wenn Sie im Ausland wohnen
• Postfachadresse — Nur für Unternehmen, für Privatpersonen leer lassen

🧭 Zur Navigation geben Sie eine Abschnittsnummer oder den DEUTSCHEN Namen eines Abschnitts, Unterabschnitts oder Feldes ein – z.B. '7', 'Kleinunternehmer-Regelung' oder 'Geburtsdatum'.

─── UNTERABSCHNITT mit Feldern (Abschnitt 4 → Natürliche Person) ───────────────

'Natürliche Person' behandelt die Kontaktdaten Ihres Steuerberaters, falls es sich
um eine Einzelperson handelt. Für die meisten Helferei-Nutzer bleibt dieser
Unterabschnitt komplett leer.

Der Unterabschnitt enthält Folgendes:
• Anrede — Anrede Ihres Steuerberaters
• Titel — Akademischer Titel, falls vorhanden
• Name — Nachname Ihres Steuerberaters
• Vorname — Vorname Ihres Steuerberaters
• Namensvorsatz — Z.B. 'von' (optional)
• Namenszusatz — Z.B. 'jr.' (optional)
• Adresse — Adresse Ihres Steuerberaters
• Telefon — Telefonnummer Ihres Steuerberaters

🧭 Zur Navigation geben Sie eine Abschnittsnummer oder den DEUTSCHEN Namen eines Abschnitts, Unterabschnitts oder Feldes ein – z.B. '7', 'Kleinunternehmer-Regelung' oder 'Geburtsdatum'.

─── FELDGRUPPE (Abschnitt 1 → Adresse → Adresse im Inland) ─────────────────────

'Adresse im Inland' enthält Ihre Wohnadresse in Deutschland. Alle Angaben müssen
exakt mit Ihrer Meldebescheinigung übereinstimmen.

Der Unterabschnitt enthält folgende Felder:
• Straße — Straßenname ohne Hausnummer, exakt wie auf der Meldebescheinigung
• Hausnummer — Hausnummer mit Zusatz falls vorhanden, z.B. '42a'
• Hausnummerzusatz — Zusatz nur wenn separat auf der Meldebescheinigung eingetragen
• Adressergänzung — Zusatzangaben falls nötig, z.B. '2. OG'
• Postleitzahl — Fünfstellige deutsche Postleitzahl
• Wohnort — Stadt oder Gemeinde, exakt wie auf der Meldebescheinigung

🧭 Zur Navigation geben Sie eine Abschnittsnummer oder den DEUTSCHEN Namen eines Abschnitts, Unterabschnitts oder Feldes ein – z.B. '7', 'Kleinunternehmer-Regelung' oder 'Geburtsdatum'.

─── FELD (Abschnitt 23 → Dateiname) ────────────────────────────────────────────

'Dateiname' ist das Feld, in dem Sie Ihr Dokument hochladen. Erlaubt sind nur
.pdf- und .xml-Dateien mit maximal 10 MB pro Datei. Laden Sie jede Datei einzeln
in einer eigenen Zeile hoch — ZIP-Archive werden abgelehnt, ebenso andere Formate
wie .doc, .jpg oder .png. Die Datei wird beim Hochladen automatisch auf Schadsoftware
geprüft.

🧭 Zur Navigation geben Sie eine Abschnittsnummer oder den DEUTSCHEN Namen eines Abschnitts, Unterabschnitts oder Feldes ein – z.B. '7', 'Kleinunternehmer-Regelung' oder 'Geburtsdatum'.
"""

FOLLOWUP_SYSTEM = """You are a helpful assistant for a German tax form (Fragebogen zur steuerlichen Erfassung für Einzelunternehmen).
The user is continuing a conversation. Reply naturally in 2-3 sentences based on the conversation history and current form position.
Be specific and actionable — if you know what the user should select or enter, tell them directly.
Do NOT list form fields or section contents. Do NOT repeat what you already said.
Do NOT start your response with '📍' or any position/breadcrumb line — that is added automatically.
Answer ONLY based on the conversation history and what the form contains. Do NOT invent information, give general tax advice, or answer questions about real-world processes outside the form. If the user asks something outside the form scope, say in one sentence that this is beyond the form and suggest they consult the relevant authority or a tax advisor.
Do NOT use numbered lists or bullet points — write in natural prose sentences.
When referring to the current form element, do not use technical terms like "field", "section", or "subsection". Instead refer to it by its name or describe it naturally — e.g. "this information", "this entry", "here you enter...", "this asks for...".
If the user's message is unclear, ask ONE short clarifying question.
When user asks about a tax or legal concept (e.g. "what is Kleinunternehmer?"),
explain it briefly in 2-3 sentences using general knowledge about German tax law.
Keep it relevant to the form context.
When answering about fields that have a spouse equivalent (like Religion, Geburtsdatum, Identifikationsnummer), 
make clear that the current field is for the taxpayer only. 
Information about the spouse goes in Section 2 ('Ehegatte / Ehegattin / eingetragene(r) Lebenspartner(in)').
If the user is on Section 23 (the last section) and asks to continue, go to next, or similar — 
tell them this is the last section and they can now review and submit the form by clicking 'Alles prüfen'.
The navigation tip will be provided in the user message — use it exactly as given."""

# ─────────────────────────────────────────────────────────────────────────────
# SESSION
# ─────────────────────────────────────────────────────────────────────────────

class Session:
    def __init__(self):
        self.lang: str = 'en'
        self.cursor: dict = FormCursor(section=1).to_dict()
        self.cursor_history: List[dict] = []
        self.last_options: List[str] = []
        self.history: List[dict] = []
        self.user_context: dict = {}
        self.pending_field_choice: dict = {}

    def add_turn(self, user: str, assistant: str):
        self.history.append({"role": "user", "content": user})
        self.history.append({"role": "assistant", "content": assistant})
        if len(self.history) > 12:
            self.history = self.history[-12:]

    def update_user_context(self, key: str, value: str):
        self.user_context[key] = value

    def get_user_context_summary(self) -> str:
        if not self.user_context:
            return ""
        lines = ["[USER CONTEXT - Persistent Info]"]
        for key, value in self.user_context.items():
            lines.append(f"- {key}: {value}")
        return "\n".join(lines)

    def push_cursor(self, old_cursor: dict):
        if old_cursor and old_cursor != {}:
            if not self.cursor_history or self.cursor_history[-1] != old_cursor:
                self.cursor_history.append(old_cursor.copy())
                if len(self.cursor_history) > 10:
                    self.cursor_history = self.cursor_history[-10:]

    def pop_cursor(self) -> dict:
        if self.cursor_history:
            return self.cursor_history.pop()
        return {}

    def cursor_breadcrumb(self) -> str:
        return FormCursor.from_dict(self.cursor).breadcrumb()


# ─────────────────────────────────────────────────────────────────────────────
# CONTEXT BUILDER
# ─────────────────────────────────────────────────────────────────────────────

class ContextBuilder:

    def __init__(self, fk: FormKnowledge):
        self.fk = fk

    def from_glossary(self, term_key: str, lang: str) -> str:
        entry = GLOSSARY.get(term_key)
        if not entry:
            return ""
        if lang == 'de':
            return f"GLOSSARY TERM: {entry['term_de']}\n\n{entry['definition_de']}"
        return (f"GLOSSARY TERM: {entry['term_en']} (DE form: \"{entry['term_de']}\")\n\n"
                f"{entry['definition_en']}")

    def _field(self, f, lang) -> str:
        label = f.field_label_en if (lang == 'en' and f.field_label_en) else f.field_label
        loc = " > ".join(filter(None, [
            f"Section {f.section_number}" if f.section_number else "",
            f.subsection_name or "", f.group_name or ""
        ]))
        lines = [
            f'FIELD: "{f.field_label}" / {label}',
            f"Location: {loc}",
            f"Type: {f.field_type}" + (" [REQUIRED]" if f.required else ""),
        ]
        exp = (f.explanation_en if lang == 'en' and f.explanation_en else f.explanation or "")
        if exp: lines.append(f"Explanation: {exp}")
        if f.options:
            lines.append("Options: " + ", ".join(f.options))
        if f.branching:
            lines.append("Branching:")
            for opt, eff in f.branching.items():
                lines.append(f"  {opt} -> {eff}")
        src = (f.source_en if lang == 'en' and f.source_en else f.source or "")
        if src: lines.append(f"Data source: {src}")
        why = (f.why_asked_en if lang == 'en' and f.why_asked_en else f.why_asked or "")
        if why: lines.append(f"Why asked: {why}")
        m = (f.common_mistakes_en if lang == 'en' and f.common_mistakes_en
             else f.common_mistakes or "")
        if m: lines.append(f"Common mistakes: {m}")
        if f.example: lines.append(f"Example: {f.example}")
        return "\n".join(lines)

    def _subsection(self, sub, lang) -> str:
        name = sub.name_en if (lang == 'en' and sub.name_en) else sub.name
        exp  = (sub.explanation_en if lang == 'en' and sub.explanation_en
                else sub.explanation or "")

        def process_field_group(fg, indent=2):
            items = []
            fg_name = fg.group_name_en if (lang == 'en' and fg.group_name_en) else fg.group_name
            exp_fg = (fg.explanation_en if lang == 'en' and fg.explanation_en else fg.explanation or "")
            exp_short = exp_fg.split('\n')[0].strip().lstrip('*').strip() if exp_fg else ""
            if exp_short:
                if lang == 'de':
                    exp_short = exp_short[0].upper() + exp_short[1:]
                else:
                    exp_short = exp_short[0].lower() + exp_short[1:]
                exp_short = exp_short.rstrip('.')
            prefix = " " * indent
            if lang == 'en' and fg_name != fg.group_name:
                line = f"{prefix}{fg.group_name} | {fg_name}"
            else:
                line = f"{prefix}{fg.group_name}"
            if exp_short:
                line += f" — {exp_short}"
            items.append(line)
            return items

        field_items = []
        for f in sub.fields:
            exp_f = (f.explanation_en if lang == 'en' and f.explanation_en else f.explanation or "")
            exp_short = exp_f.split('\n')[0].strip().lstrip('*').strip() if exp_f else ""
            if exp_short:
                if lang == 'de':
                    exp_short = exp_short[0].upper() + exp_short[1:]
                else:
                    exp_short = exp_short[0].lower() + exp_short[1:]
                exp_short = exp_short.rstrip('.')
            if lang == 'en' and f.field_label_en:
                line = f"{f.field_label} | {f.field_label_en}"
            else:
                line = f.field_label
            if exp_short:
                line += f" — {exp_short}"
            field_items.append(line)
        for fg in sub.field_groups:
            field_items.extend(process_field_group(fg))

        nested_sub_items = []
        if hasattr(sub, 'subsections') and sub.subsections:
            for nested_sub in sub.subsections:
                nested_name = nested_sub.name_en if (lang == 'en' and nested_sub.name_en) else nested_sub.name
                field_count = len(nested_sub.fields)
                nested_sub_items.append(f"  {nested_sub.name} ({nested_name}) [subsection with {field_count} fields]")

        lines = [f'SUBSECTION: "{sub.name}" / {name}', f"Section: {sub.section_number}"]
        if exp: lines.append(f"Description: {exp}")

        total_items = len(sub.fields) + len(sub.field_groups)
        if hasattr(sub, 'subsections'):
            total_items += len(sub.subsections)

        if field_items or nested_sub_items:
            content_desc = f"Content ({total_items} items - {len(sub.fields)} direct fields"
            if sub.field_groups:
                content_desc += f", {len(sub.field_groups)} field groups"
            if hasattr(sub, 'subsections') and sub.subsections:
                content_desc += f", {len(sub.subsections)} subsections"
            content_desc += "):"
            lines.append(content_desc)
            for item in field_items:
                lines.append(f"  {item}")
            for item in nested_sub_items:
                lines.append(item)

        return "\n".join(lines)

    def _section(self, sec, lang) -> str:
        name = sec.name_en if (lang == 'en' and sec.name_en) else sec.name
        exp  = (sec.explanation_en if lang == 'en' and sec.explanation_en
                else sec.explanation or "")

        items = []
        for f in sec.fields:
            exp_f = (f.explanation_en if lang == 'en' and f.explanation_en else f.explanation or "")
            exp_short = exp_f.split('\n')[0].strip().lstrip('*').strip() if exp_f else ""
            if exp_short:
                if lang == 'de':
                    exp_short = exp_short[0].upper() + exp_short[1:]
                else:
                    exp_short = exp_short[0].lower() + exp_short[1:]
                exp_short = exp_short.rstrip('.')
            if lang == 'en' and f.field_label_en and f.field_label_en != f.field_label:
                line = f"{f.field_label} | {f.field_label_en}"
            else:
                line = f.field_label
            if exp_short:
                line += f" — {exp_short}"
            items.append(line)

        for fg in sec.field_groups:
            if lang == 'en' and fg.group_name_en and fg.group_name_en != fg.group_name:
                items.append(f"{fg.group_name} | {fg.group_name_en}")
            else:
                items.append(fg.group_name)

        subs = []
        for s in sec.subsections:
            exp_s = (s.explanation_en if lang == 'en' and s.explanation_en else s.explanation or "")
            # Take only first line of explanation
            exp_short = exp_s.split('\n')[0].strip().lstrip('*').strip() if exp_s else ""
            if exp_short:
                if lang == 'de':
                    exp_short = exp_short[0].upper() + exp_short[1:]
                else:
                    exp_short = exp_short[0].lower() + exp_short[1:]
                exp_short = exp_short.rstrip('.')
            if lang == 'en':
                line = f"  {s.name} | {s.name_en}"
            else:
                line = f"  {s.name}"
            if exp_short:
                line += f" — {exp_short}"
            subs.append(line)

        lines = [f'SECTION {sec.number}: "{sec.name}" / {name}']
        if exp: lines.append(f"Description: {exp}")

        total = len(sec.fields) + len(sec.field_groups) + len(sec.subsections)
        lines.append(f"⚠️ TOTAL ITEMS TO LIST: {total}. List EXACTLY these items — nothing more, nothing less.")

        if items: lines.append("Direct contents:\n  " + "\n  ".join(items))
        if subs:  lines.append("Subsections:\n" + "\n".join(subs))
        return "\n".join(lines)

    def _field_group(self, fg, lang) -> str:
        name = fg.group_name_en if (lang == 'en' and fg.group_name_en) else fg.group_name
        exp  = (fg.explanation_en if lang == 'en' and fg.explanation_en
                else fg.explanation or "")

        loc_parts = []
        if hasattr(fg, 'section_number') and fg.section_number:
            loc_parts.append(f"Section {fg.section_number}")
        if hasattr(fg, 'subsection_name') and fg.subsection_name:
            loc_parts.append(fg.subsection_name)
        if hasattr(fg, 'parent_group_name') and fg.parent_group_name:
            loc_parts.append(fg.parent_group_name)

        lines = [f'FIELD GROUP: "{fg.group_name}" / {name}']
        if loc_parts: lines.append(f"Location: {' > '.join(loc_parts)}")
        if exp: lines.append(f"Description: {exp}")

        if hasattr(fg, 'field_groups') and fg.field_groups:
            nested_items = []
            for nested_fg in fg.field_groups:
                nested_name_en = nested_fg.group_name_en if (lang == 'en' and nested_fg.group_name_en) else None
                if lang == 'en' and nested_name_en and nested_name_en != nested_fg.group_name:
                    nested_items.append(f"{nested_fg.group_name} ({nested_name_en}) - {len(nested_fg.fields)} fields")
                else:
                    nested_items.append(f"{nested_fg.group_name} - {len(nested_fg.fields)} fields")
            if nested_items:
                lines.append("Contains:")
                for item in nested_items:
                    lines.append(f"  • {item}")
        elif fg.fields:
            if lang == 'en':
                lines.append("Fields: " + ", ".join(
                    f"{f.field_label} | {f.field_label_en}" if f.field_label_en else f.field_label
                    for f in fg.fields
                ))
            else:
                lines.append("Fields: " + ", ".join(f.field_label for f in fg.fields))

        return "\n".join(lines)


# ─────────────────────────────────────────────────────────────────────────────
# AGENT
# ─────────────────────────────────────────────────────────────────────────────

class TaxFormAgent:
    VERSION = "1.0.0"

    _NEXT_KEYWORDS = {
        "next section", "continue to next section",
        "nächster abschnitt", "nächste sektion", "weiter zum nächsten abschnitt",
        "next", "weiter",
        "ok let's continue", "let's continue", "proceed", "proceed to next section",
        "move to next", "ok next", "ok weiter"
    }
    _PREV_KEYWORDS = {
        "previous section", "back to previous section",
        "vorheriger abschnitt", "vorherige sektion", "zurück zum vorherigen abschnitt"
    }

    def __init__(self, form_knowledge: FormKnowledge, llm_client: LLMClient):
        self.fk  = form_knowledge
        self.llm = llm_client
        #self.ld  = LanguageDetector()
        self.ctx = ContextBuilder(form_knowledge)
        self._sessions: Dict[str, Session] = {}

    # ── Session management ────────────────────────────────────────────────────

    def _s(self, tid: str) -> Session:
        if tid not in self._sessions:
            self._sessions[tid] = Session()
        return self._sessions[tid]

    def reset(self, tid: str):
        self._sessions[tid] = Session()

    def set_lang(self, l, tid):
        self._s(tid).lang = l if l in ('de', 'en') else 'en'

    def get_cursor(self, tid) -> str:
        return self._s(tid).cursor_breadcrumb()

    # ── Main entry point ──────────────────────────────────────────────────────

    def chat(self, user_input: str, thread_id: str = "default") -> str:
        s = self._s(thread_id)

        cmd_result = self._handle_command(user_input, s)
        if cmd_result is not None:
            return cmd_result

        # Sanitize input
        user_input = user_input[:400].strip()
        if not user_input:
            return ""
        if user_input.startswith('{') and user_input.endswith('}'):
            user_input = re.sub(r'[{}":]', '', user_input).strip()

        # Preprocess: "• German | English — desc" → "German"
        _text = user_input.strip().lstrip('•').strip()
        if '|' in _text:
            _text = _text.split('|')[0].strip()
        # Preprocess: "'GermanName' (EnglishName)" → "GermanName"
        _text = re.sub(r"^'([^']+)'\s*\(.*\)\s*$", r'\1', _text)
        user_input = _text
        print("[DEBUG preprocess]", repr(user_input))

        # Step 1: Parse intent
        intent, query, lang, confusion, sec_hint, cur_move, user_ctx_update = self._parse_intent(user_input, s)

        # Step 1.7: Convert follow_up to navigate if query exactly matches a form item
        if intent == INTENT_FOLLOWUP and s.cursor.get('section'):
            _cur = FormCursor.from_dict(s.cursor)
            _results = self.fk.search(query, lang, section_filter=_cur.section)
            _exact = [r for r in _results if r['score'] == 100]
            if len(_exact) == 1 and _exact[0]['type'] in ('field', 'subsection', 'field_group'):
                intent = INTENT_NAVIGATE
            elif len(_exact) > 1:
                msg = self._build_disambig_message(_exact, query, _cur, lang)
                s.add_turn(user_input, msg)
                return msg

        # Step 2: Handle cursor movement (next/up/reset)
        cursor = self._apply_cursor_move(cur_move, sec_hint, intent, query, s)

        # Next on last section
        if cur_move == 'next' and cursor.section == 23 and FormCursor.from_dict(s.cursor).section == 23:
            msg = ("Das war der letzte Abschnitt. Klicken Sie nun auf 'Alles prüfen', um alle Angaben zu überprüfen, bevor Sie den Fragebogen ans Finanzamt übermitteln."
                if s.lang == 'de' else
                "That was the last section. Please click 'Alles prüfen' to review all your entries before submitting the form to the tax office.")
            bc = self._format_breadcrumb(FormCursor.from_dict(s.cursor), s.lang)
            if bc:
                msg = f"📍 {bc}\n\n{msg}"
            s.add_turn(user_input, msg)
            return msg

        # Step 3: Parse arrow-path navigation
        path_done, intent, query, cursor, context_cursor = self._parse_arrow_path(
            intent, query, cursor, lang, s
        )

        if not path_done:
            context_cursor = cursor

        # Step 5: Cross-section disambiguation (before cursor update)
        if not path_done and intent == INTENT_NAVIGATE and cursor.section and cur_move not in ('next', 'up'):
            result = self._cross_section_disambig(intent, query, cursor, lang, user_input, s)
            if result is not None:
                return result

        # Step 6: Handle pending field choice
        if s.pending_field_choice:
            result = self._handle_pending_choice(query, cursor, lang, user_input, sec_hint, s)
            if result is not None:
                return result

        # Step 7: Update cursor for navigation
        if not path_done and intent == INTENT_NAVIGATE:
            if cur_move in ('next', 'up'):
                # Cursor already updated in _apply_cursor_move, write to session
                s.push_cursor(s.cursor)
                s.cursor = cursor.to_dict()
                context_cursor = FormCursor.from_dict(s.cursor)
            else:
                result = self._navigate_and_disambig(intent, query, cursor, lang, user_input, s)
                if result is not None:
                    return result
                context_cursor = FormCursor.from_dict(s.cursor)

        # Step 8: Fetch context
        context_str = self._fetch_context(intent, query, lang, context_cursor, confusion)

        # Step 9: Update cursor for non-navigate intents
        if not path_done and intent not in (INTENT_NAVIGATE, INTENT_DIAGNOSE, INTENT_FOLLOWUP):
            if query.strip():
                result = self._update_cursor_non_navigate(intent, query, cursor, lang, user_input, s)
                if result is not None:
                    return result

        # Step 10: Build and return answer
        return self._build_answer(user_input, context_str, intent, confusion, cur_move, lang, s)

    # ── Command handling ──────────────────────────────────────────────────────

    def _handle_command(self, user_input: str, s: Session) -> Optional[str]:
        if not user_input.strip().startswith('/'):
            return None
        cmd = user_input.strip().lower()
        if cmd.startswith('/lang '):
            target = cmd.replace('/lang ', '').strip()
            if target in ('de', 'en'):
                s.lang = target
                return "Sprache auf Deutsch umgestellt. ✓" if target == 'de' else "Language switched to English. ✓"
            return "Ungültige Sprache. Bitte /lang de oder /lang en" if s.lang == 'de' else "Invalid language. Use: /lang de or /lang en"
        return None

    # ── Intent parsing ────────────────────────────────────────────────────────

    def _parse_intent(self, user_input: str, s: Session):
        """Parse user input into intent, query, and metadata."""
        t = user_input.strip().lower()

        if t in self._NEXT_KEYWORDS:
            return INTENT_NAVIGATE, "", s.lang, None, None, "next", None
        if t in self._PREV_KEYWORDS:
            return INTENT_NAVIGATE, "", s.lang, None, None, "up", None

        # Breadcrumb paste — restore cursor directly
        breadcrumb_match = re.match(r'^📍\s*(?:Section|Abschnitt)\s+(\d+):', user_input.strip())
        if breadcrumb_match:
            sec_num = int(breadcrumb_match.group(1))
            if sec_num in self.fk.sections:
                parts = [p.strip() for p in user_input.split('→')]
                cursor = FormCursor(section=sec_num)
                for part in parts[1:]:
                    part_clean = part.strip()
                    results = self.fk.search(part_clean, s.lang,
                                            section_filter=sec_num,
                                            current_section=cursor.section,
                                            current_subsection=cursor.subsection)
                    good = [r for r in results if r['score'] >= 40]
                    if good:
                        cursor = FormCursor.from_dict(
                            self._make_cursor_from_result(good[0], cursor)
                        )
                # If field_group and last part matches its name — find the field inside
                if cursor.field_group and not cursor.field:
                    last_part = parts[-1].strip()
                    fg_count = sum(1 for p in parts if p.strip() == cursor.field_group)
                    if last_part == cursor.field_group and fg_count >= 2:
                        fg_obj = self.fk.get_field_group(
                            cursor.section,
                            cursor.subsection,
                            cursor.field_group
                        )
                        if fg_obj:
                            matching_field = next(
                                (f for f in fg_obj.fields if f.field_label == cursor.field_group),
                                None
                            )
                            if matching_field:
                                cursor = FormCursor(
                                    section=cursor.section,
                                    subsection=cursor.subsection,
                                    field_group=cursor.field_group,
                                    field=matching_field.field_name
                                )
                s.push_cursor(s.cursor)
                s.cursor = cursor.to_dict()
                # Return INTENT_EXPLAIN so Step 7 does not overwrite the cursor
                return INTENT_EXPLAIN, "", s.lang, None, None, None, None

        # LLM parsing
        ctx = f"Current form position: {s.cursor_breadcrumb()}. Current conversation language: {s.lang}"
        if s.user_context:
            ctx += f". User context: {s.get_user_context_summary()}"

        result = self.llm.complete_json(
            messages=[{"role": "user", "content": f"[Context: {ctx}]\n\nUser message: {user_input}"}],
            system=UNDERSTAND_SYSTEM,
            max_tokens=200,
        )

        if "error" in result:
            #lang = self.ld.detect(user_input)
            return INTENT_EXPLAIN, user_input, s.lang, None, None, None, None

        if result.get('intent') == 'clarify':
            result['intent'] = INTENT_NAVIGATE

        query = self._restore_query(result, user_input)

        # Clean query
        query = re.sub(r'^[\s•\-–—\'\"\„\"\"\«\»]+', '', query).strip()
        query = re.sub(r'\s*[|—]\s*.+$', '', query).strip()
        query = re.sub(r'\s*\|\s*$', '', query).strip()
        query = re.sub(r'[\s\'\"\„\"\"\«\»]+$', '', query).strip()

        intent  = result.get('intent', INTENT_EXPLAIN)
        if intent not in VALID_INTENTS:
            intent = INTENT_FOLLOWUP
        #lang    = result.get('language') or self.ld.detect(user_input)
        lang = result.get('language') or s.lang
        confusion = result.get('detected_confusion')
        sec_hint  = result.get('section_hint')
        cur_move  = result.get('cursor_move')
        user_ctx  = result.get('user_context_update')

        if intent == INTENT_EXPLAIN:
            cur_move = None

        sect_match = re.match(r'^(?:sec|absch)[a-z]*\s*(\d+)$', query.strip().lower())
        if sect_match:
            sec_num = int(sect_match.group(1))
            if sec_num in self.fk.sections:
                query = str(sec_num)
                intent = INTENT_NAVIGATE
                sec_hint = sec_num

        if intent == INTENT_FOLLOWUP:
            q_lower = query.strip().lower()
            if len(q_lower) >= 4:
                found = self.fk.search(q_lower, 'de')
                if found and found[0]['score'] >= 60:
                    intent = INTENT_NAVIGATE

        if user_ctx and isinstance(user_ctx, dict):
            for key, value in user_ctx.items():
                s.update_user_context(key, value)
        print(f"[understand] intent={intent} query={repr(query)} lang={lang} cursor_move={cur_move}")
        return intent, query, lang, confusion, sec_hint, cur_move, user_ctx

    def _restore_query(self, result: dict, user_input: str) -> str:
        """Restore original user input as query when appropriate."""
        q_llm  = (result.get('query') or '').lower()
        q_orig = user_input.strip().lower()

        if q_llm and q_orig.startswith(q_llm) and q_llm != q_orig:
            result['query'] = user_input.strip()

        q = result.get('query') or ''
        q = re.sub(r'^[\s•\-–—\'\"]+', '', q)
        q = re.sub(r'[\s\'\"]+$', '', q)
        if q:
            result['query'] = q

        if result.get('intent') == INTENT_NAVIGATE:
            orig = user_input.strip()
            orig_lower = orig.lower()
            # Arrow path — always restore original
            if '→' in orig:
                result['query'] = orig
            # Single digit — always use original, do not normalize
            elif orig.isdigit():
                result['query'] = orig
            elif (orig_lower.startswith('section ') or orig_lower.startswith('abschnitt ') or
                    re.match(r'^sec\w*\s+\d+$', orig_lower) or
                    re.match(r'^abschn\w*\s+\d+$', orig_lower)):
                pass  # keep LLM normalization
            else:
                result['query'] = orig

        return result.get('query') or user_input

    # ── Cursor movement ───────────────────────────────────────────────────────

    def _apply_cursor_move(self, cur_move: Optional[str], sec_hint: Optional[int],
                           intent: str, query: str, s: Session) -> FormCursor:
        """Apply cursor_move (next/up/reset) and section_hint."""
        cursor = FormCursor.from_dict(s.cursor)

        if cur_move == "reset":
            cursor = FormCursor(section=1)
            s.cursor_history = []

        elif cur_move == "up":
            current_sec = cursor.section or 1
            prev_sec = current_sec - 1
            if prev_sec >= 1 and prev_sec in self.fk.sections:
                s.push_cursor(s.cursor)
                cursor = FormCursor(section=prev_sec)

        elif cur_move == "next":
            if query.strip():
                pass  # query not empty — LLM mistake, ignore next
            else:
                cursor = self._move_next(cursor, s)

        if sec_hint:
            if intent == INTENT_NAVIGATE:
                cursor = FormCursor(section=sec_hint)
            elif not cursor.section:
                cursor.section = sec_hint

        return cursor

    def _move_next(self, cursor: FormCursor, s: Session) -> FormCursor:
        next_sec = (cursor.section or 0) + 1
        if next_sec in self.fk.sections:
            s.push_cursor(s.cursor)
            return FormCursor(section=next_sec)
        return cursor

    # ── Arrow-path parsing ────────────────────────────────────────────────────

    def _parse_arrow_path(self, intent: str, query: str, cursor: FormCursor,
                          lang: str, s: Session):
        """Parse 'Part1 → Part2 → Part3' navigation paths."""
        if '→' not in query or intent != INTENT_NAVIGATE:
            return False, intent, query, cursor, cursor

        path_parts = [p.strip() for p in query.split('→')]
        if len(path_parts) <= 1:
            return False, intent, query, path_parts[-1] if path_parts else query, cursor

        temp_cursor = cursor

        for part in path_parts[:-1]:
            sec_match = re.match(r'^section\s+(\d+)', part.strip().lower())
            if sec_match:
                sec_num = int(sec_match.group(1))
                if sec_num in self.fk.sections:
                    temp_cursor = FormCursor(section=sec_num)

            part_clean = re.sub(r'^section\s+\d+:\s*', '', part.strip().lower())
            part_clean = part.strip() if not part_clean else part_clean

            if not sec_match:
                for sn, sec in self.fk.sections.items():
                    if sec.name.lower() == part_clean.lower():
                        temp_cursor = FormCursor(section=sn)
                        break

            part_results = self.fk.search(
                part_clean, lang,
                section_filter=temp_cursor.section if temp_cursor.section else None,
                current_section=temp_cursor.section,
                current_subsection=temp_cursor.subsection,
                current_field_group=temp_cursor.field_group
            )
            good = [r for r in part_results if r['score'] >= 50]
            if good:
                if temp_cursor.subsection:
                    same_sub = [r for r in good if r.get('subsection') == temp_cursor.subsection]
                    if same_sub:
                        good = same_sub
                new_c = self._make_cursor_from_result(good[0], temp_cursor)
                temp_cursor = FormCursor.from_dict(new_c)

        last_part = path_parts[-1].strip()
        last_results = self.fk.search(
            last_part, lang,
            section_filter=temp_cursor.section if temp_cursor.section else None,
            current_section=temp_cursor.section,
            current_subsection=temp_cursor.subsection,
            current_field_group=temp_cursor.field_group
        )
        last_good = [r for r in last_results if r['score'] >= 50]

        if last_good:
            exact_sub = [r for r in last_good if r.get('subsection') == temp_cursor.subsection]
            if temp_cursor.subsection:
                fields_in_sub = [r for r in exact_sub if r['type'] == 'field']
                if fields_in_sub:
                    exact_sub = fields_in_sub
            # If last_part matches field_group name — find the field inside explicitly
            if temp_cursor.field_group and last_part.strip() == temp_cursor.field_group:
                fg_obj = self.fk.get_field_group(
                    temp_cursor.section,
                    temp_cursor.subsection,
                    temp_cursor.field_group
                )
                if fg_obj:
                    fields_in_fg = [
                        f for f in fg_obj.fields
                        if f.field_label == last_part.strip() or f.field_label_en == last_part.strip()
                    ]
                    if fields_in_fg:
                        f = fields_in_fg[0]
                        new_cursor_dict = {
                            'section': temp_cursor.section,
                            'subsection': temp_cursor.subsection,
                            'parent_subsection': None,
                            'field_group': temp_cursor.field_group,
                            'field': f.field_name
                        }
                        s.push_cursor(s.cursor)
                        s.cursor = new_cursor_dict
                        s.last_options = []
                        context_cursor = FormCursor.from_dict(new_cursor_dict)
                        return True, INTENT_EXPLAIN, last_part, temp_cursor, context_cursor
            chosen = exact_sub[0] if exact_sub else last_good[0]
            s.push_cursor(s.cursor)
            new_cursor_dict = self._make_cursor_from_result(chosen, temp_cursor)
            s.cursor = new_cursor_dict
            s.last_options = []
            context_cursor = FormCursor.from_dict(new_cursor_dict)
            return True, INTENT_EXPLAIN, last_part, temp_cursor, context_cursor
        else:
            return False, intent, last_part, temp_cursor, temp_cursor

    # ── Cross-section disambiguation ──────────────────────────────────────────

    def _cross_section_disambig(self, intent: str, query: str, cursor: FormCursor,
                                lang: str, user_input: str, s: Session) -> Optional[str]:
        """Show disambiguation list when field not found in current section."""
        if query.strip().isdigit():
            return None

        section_results = self.fk.search(
            query, lang,
            section_filter=cursor.section,
            current_section=cursor.section,
            current_subsection=cursor.subsection,
            current_field_group=cursor.field_group
        )
        good_results = [r for r in section_results if r['score'] >= 30]

        if good_results:
            return None

        all_results = self.fk.search(query, lang)
        other_results = [r for r in all_results
                         if r['score'] >= 50 and r['section'] != cursor.section]

        if not other_results:
            return None

        sections_map = defaultdict(list)
        seen_keys = set()
        for r in other_results:
            sn  = r['section']
            sub = r.get('subsection') or ''
            fg  = r.get('field_group') or r.get('group') or ''
            if r['type'] == 'field':
                key = (sn, sub, fg, r['object'].field_name)
            elif r['type'] == 'field_group':
                key = (sn, sub, r['object'].group_name)
            else:
                key = (sn, sub)
            if key not in seen_keys:
                seen_keys.add(key)
                sections_map[sn].append(r)

        def sort_key(r):
            sn   = r['section']
            sub  = r.get('subsection') or ''
            fg   = r.get('field_group') or r.get('group') or ''
            name = (r['object'].field_label if r['type'] == 'field' else
                    r['object'].group_name if r['type'] == 'field_group' else
                    getattr(r['object'], 'name', ''))
            depth = len([x for x in [sub, fg, name] if x])
            return (sn, sub, depth, fg, name)

        locations = []
        for sn in sorted(sections_map.keys()):
            for r in sorted(sections_map[sn], key=sort_key):
                locations.append({
                    'section': r['section'], 'subsection': r.get('subsection'),
                    'field_group': r.get('field_group'),
                    'type': r['type'], 'object': r['object']
                })
        s.pending_field_choice = {'field_name': query, 'locations': locations}

        if lang == 'de':
            msg = f"'{query}' existiert nicht in Abschnitt {cursor.section}, aber ich habe es gefunden in:\n\n"
        else:
            msg = f"'{query}' does not exist in Section {cursor.section}, but I found it in:\n\n"

        MAX_RESULTS = 10
        total = sum(len(v) for v in sections_map.values())
        count = 0
        for sn in sorted(sections_map.keys()):
            sec = self.fk.get_section(sn)
            if not sec:
                continue
            for r in sorted(sections_map[sn], key=sort_key):
                if count >= MAX_RESULTS:
                    break
                msg += f"• {self._format_result_path(r, sec, include_section=True, lang=lang)}\n"
                count += 1
            if count >= MAX_RESULTS:
                break

        if total > MAX_RESULTS:
            remaining = total - MAX_RESULTS
            msg += (f"\n...and {remaining} more results. Please be more specific."
                    if lang == 'en' else
                    f"\n...und {remaining} weitere Ergebnisse. Bitte präzisieren Sie Ihre Suche.")

        msg += "\nWhich section would you like to go to?" if lang == 'en' else "\nZu welchem Abschnitt möchten Sie wechseln?"

        bc = self._format_breadcrumb(FormCursor.from_dict(s.cursor), lang)
        if bc:
            msg = f"📍 {bc}\n\n" + msg

        s.add_turn(user_input, msg)
        return msg

    # ── Pending field choice ──────────────────────────────────────────────────

    def _handle_pending_choice(self, query: str, cursor: FormCursor, lang: str,
                               user_input: str, sec_hint: Optional[int], s: Session) -> Optional[str]:
        """Handle user response to cross-section disambiguation."""
        current_sec = FormCursor.from_dict(s.cursor).section
        has_local = False
        if current_sec:
            check = self.fk.search(query, lang, section_filter=current_sec)
            has_local = bool([r for r in check if r['score'] >= 30])

        should_clear = (
            '→' in user_input or
            query.strip().isdigit() or
            sec_hint is not None or
            re.match(r'^(?:sec|abschn)[a-z]*\s*\d+$', query.strip().lower()) or
            has_local
        )
        if should_clear:
            s.pending_field_choice = {}
            return None

        # If query matches well globally outside pending sections — clear pending
        all_results = self.fk.search(query, lang)
        good_global = [r for r in all_results if r['score'] >= 40]
        pending_sections = {loc['section'] for loc in s.pending_field_choice.get('locations', [])}
        if good_global and good_global[0]['section'] not in pending_sections:
            s.pending_field_choice = {}
            return None

        locations = s.pending_field_choice['locations']
        user_answer = query.lower().strip()
        numbers = re.findall(r'\d+', user_answer)
        matched = None

        for loc in locations:
            sn  = loc['section']
            sec = self.fk.get_section(sn)
            if not sec:
                continue
            if (str(sn) in numbers or
                    sec.name.lower() in user_answer or
                    (sec.name_en or '').lower() in user_answer or
                    (loc.get('subsection') and loc['subsection'].lower() in user_answer)):
                matched = loc
                break

        if matched:
            new_cursor = FormCursor(section=matched['section'])
            s.push_cursor(s.cursor)
            s.cursor = new_cursor.to_dict()
            s.last_options = []
            s.pending_field_choice = {}
            ctx_str = self._fetch_context(INTENT_NAVIGATE, str(matched['section']), lang, new_cursor, None)
            final_cur = FormCursor.from_dict(s.cursor)
            answer = self._explain(str(matched['section']), ctx_str, lang, INTENT_NAVIGATE,
                                   None, self._format_breadcrumb(final_cur, lang),
                                   s.history, s.get_user_context_summary(), cursor_type='section')
            bc = self._format_breadcrumb(final_cur, lang)
            if bc:
                answer = f"📍 {bc}\n\n{answer}"
            s.add_turn(user_input, answer)
            return answer
        else:
            answer = ("Sorry, I couldn't match that to any option. Please type the full name to navigate there."
                      if lang == 'en' else
                      "Entschuldigung, konnte nicht zuordnen. Bitte geben Sie den vollständigen Namen ein.")
            s.add_turn(user_input, answer)
            return answer

    # ── Navigate and disambiguate ─────────────────────────────────────────────

    def _navigate_and_disambig(self, intent: str, query: str, cursor: FormCursor,
                            lang: str, user_input: str, s: Session) -> Optional[str]:
        """Update cursor for navigate intent; return disambiguation message if needed."""
        new_cursor, new_options = self._update_cursor(intent, query, cursor, lang)

        if isinstance(new_cursor, dict) and new_cursor.get('ambiguous'):
            options = new_cursor['options']

            # If already on a subsection and best result is in it — navigate directly
            if cursor.subsection:
                same_sub = [r for r in options if r.get('subsection') == cursor.subsection]
                other_sub = [r for r in options if r.get('subsection') != cursor.subsection]
                if (same_sub and len(same_sub) == 1 and
                        (not other_sub or same_sub[0]['score'] >= other_sub[0]['score'] * 1.2)):
                    best = same_sub[0]
                    new_c = self._make_cursor_from_result(best, cursor)
                    if new_c != s.cursor:
                        s.push_cursor(s.cursor)
                    s.cursor = new_c
                    s.last_options = []
                    return None

            # If query is a clear substring of exactly one option — navigate directly
            query_norm = query.lower().replace(" ", "").replace("-", "")

            def get_label(obj):
                if hasattr(obj, 'field_label'):
                    return obj.field_label
                if hasattr(obj, 'subsection_name'):
                    return obj.subsection_name
                return ''

            def query_in_name(r):
                return query_norm in get_label(r['object']).lower().replace(" ", "").replace("-", "")

            substring_matches = [r for r in options if query_in_name(r)]
            if len(query_norm) >= 5 and len(substring_matches) == 1:
                best = substring_matches[0]
                new_c = self._make_cursor_from_result(best, cursor)
                if new_c != s.cursor:
                    s.push_cursor(s.cursor)
                s.cursor = new_c
                s.last_options = []
                return None

            msg = self._build_disambig_message(options, query, cursor, lang)
            s.add_turn(user_input, msg)
            return msg

        if new_cursor != s.cursor:
            s.push_cursor(s.cursor)
        s.cursor = new_cursor
        s.last_options = new_options
        return None

    def _build_disambig_message(self, options: list, query: str, cursor: FormCursor, lang: str) -> str:
        """Build disambiguation message for ambiguous results."""
        bc = self._format_breadcrumb(cursor, lang)
        if lang == 'de':
            msg = f"📍 {bc}\n\n" if bc else ""
            sec_label = f"Abschnitt {cursor.section}" if cursor.section else "der Form"
            msg += f"Ich habe mehrere passende Einträge für '{query}' in {sec_label} gefunden:\n\n"
        else:
            msg = f"📍 {bc}\n\n" if bc else ""
            sec_label = f"Section {cursor.section}" if cursor.section else "the form"
            msg += f"I found several items matching '{query}' in {sec_label}:\n\n"

        seen_names = set()
        deduped = []
        for r in options:
            obj = r['object']
            if r['type'] == 'field':
                key = f"{r.get('subsection','')}/{r.get('group','')}/{obj.field_label}"
            elif r['type'] == 'field_group':
                key = f"{r.get('subsection','')}/{obj.group_name}"
            elif r['type'] == 'subsection':
                key = obj.name
            else:
                key = str(obj)
            if key not in seen_names:
                seen_names.add(key)
                deduped.append(r)

        deduped.sort(key=lambda r: (
            len(r.get('subsection') or '') + len(r.get('group') or ''),
            r['object'].name if r['type'] == 'subsection' else
            r['object'].group_name if r['type'] == 'field_group' else
            r['object'].field_label if r['type'] == 'field' else ''
        ))

        sec = self.fk.get_section(cursor.section) if cursor.section else None
        for r in deduped[:MAX_DISAMBIG_RESULTS]:
            path = self._format_result_path(r, sec, include_section=True, lang=lang)
            if path.strip():
                msg += f"• {path}\n"

        msg += "\nBitte geben Sie den vollständigen Namen ein." if lang == 'de' else "\nPlease type the full name to navigate there."
        return msg

    # ── Update cursor for non-navigate intents ────────────────────────────────

    def _update_cursor_non_navigate(self, intent: str, query: str, cursor: FormCursor,
                                    lang: str, user_input: str, s: Session) -> Optional[str]:
        """Update cursor for explain_field intent; return message if cross-section."""
        new_cursor, new_options = self._update_cursor(intent, query, cursor, lang)

        if intent == INTENT_EXPLAIN and cursor.section:
            all_results = self.fk.search(
                query, lang,
                section_filter=cursor.section,
                current_section=cursor.section,
                current_subsection=cursor.subsection,
                current_field_group=cursor.field_group
            )
            field_results = [r for r in all_results if r['type'] == 'field' and r['score'] >= 80]

            def matches_current(r):
                if r['section'] != cursor.section:
                    return False
                if cursor.field_group and r.get('group') == cursor.field_group:
                    return True
                if cursor.subsection:
                    return r.get('subsection') == cursor.subsection or r.get('section') == cursor.section
                return True

            current_has_field = any(matches_current(r) for r in field_results)
            other_sections = [r for r in field_results if r['section'] != cursor.section]

            if not current_has_field and len(other_sections) >= 1:
                locations = [{'section': r['section'], 'subsection': r.get('subsection'),
                              'field_group': r.get('field_group')}
                             for r in field_results]
                s.pending_field_choice = {'field_name': field_results[-1]['object'].field_name, 'locations': locations}

                if lang == 'de':
                    msg = f"Das Feld '{query}' existiert nicht in Abschnitt {cursor.section}, aber ich habe es gefunden in:\n\n"
                else:
                    msg = f"The field '{query}' does not exist in your current section (Section {cursor.section}), but I found it in:\n\n"

                for r in field_results:
                    sec = self.fk.get_section(r['section'])
                    if sec:
                        section_label = "Abschnitt" if lang == 'de' else "Section"
                        loc_str = f"• {section_label} {r['section']}: {sec.name}"
                        if r.get('subsection'):
                            loc_str += f" > {r['subsection']}"
                        msg += f"{loc_str}\n"

                msg += "\nZu welchem Abschnitt möchten Sie wechseln?" if lang == 'de' else "\nWhich section would you like to go to?"
                s.add_turn(user_input, msg)
                return msg

        if new_cursor != s.cursor:
            s.push_cursor(s.cursor)
        s.cursor = new_cursor
        s.last_options = new_options
        return None

    # ── Context fetching ──────────────────────────────────────────────────────

    def _fetch_context(self, intent, query, lang, cursor, confusion) -> str:
        parts = []

        # follow_up — no context needed, handled via FOLLOWUP_SYSTEM + history
        if intent == INTENT_FOLLOWUP:
            if cursor.section:
                q_lower = query.lower()
                has_question = any(w in q_lower for w in ['was', 'wo', 'wie', 'welch', 'what', 'where', 'how', 'which'])
                has_next     = any(w in q_lower for w in ['weiter', 'nächste', 'dann', 'next', 'continue', 'then', 'after'])
                if has_question and has_next:
                    next_sec = self.fk.sections.get(cursor.section + 1)
                    if next_sec:
                        parts.append(f"Next section: {self.ctx._section(next_sec, lang)}")
                elif has_next and cursor.section == 23:
                    sec23 = self.fk.get_section(23)
                    if sec23:
                        exp = (sec23.explanation_en if lang == 'en' else sec23.explanation) or ""
                        last_para = exp.strip().split('\n\n')[-1].strip()
                        parts.append(f"[FINAL INSTRUCTIONS]\n{last_para}")
                elif cursor.section == 23 and self.fk.final_instructions:
                    fi = self.fk.final_instructions
                    key_t = 'title' if lang == 'de' else 'title_en'
                    key_x = 'text_de' if lang == 'de' else 'text_en'
                    parts.append(f"[FINAL INSTRUCTIONS]\n{fi.get(key_t, '')}\n\n{fi.get(key_x, '')}")
            return "\n\n===\n\n".join(filter(None, parts))

        # Confusion glossary
        if confusion:
            gkey = {"umsatz_gewinn": "umsatz_gewinn", "steuernummer_ust": "steuernummer",
                    "estimate_vs_fact": "umsatz_gewinn"}.get(confusion)
            if gkey:
                gc = self.ctx.from_glossary(gkey, lang)
                if gc:
                    parts.append(gc)

        # Render what is at cursor position
        if cursor.field:
            results = self.fk.search(
                cursor.field, lang,
                section_filter=cursor.section,
                current_section=cursor.section,
                current_subsection=cursor.subsection,
                current_field_group=cursor.field_group
            )
            field_results = [r for r in results if r['type'] == 'field' and r['object'].field_name == cursor.field]
            if field_results:
                parts.append(self.ctx._field(field_results[0]['object'], lang))
        elif cursor.field_group:
            fg = self.fk.get_field_group(cursor.section, cursor.subsection, cursor.field_group)
            if fg:
                parts.append(self.ctx._field_group(fg, lang))
        elif cursor.subsection:
            sub = self.fk.get_subsection(cursor.section, cursor.subsection)
            if sub:
                parts.append(self.ctx._subsection(sub, lang))
        elif cursor.section:
            sec = self.fk.get_section(cursor.section)
            if sec:
                parts.append(self.ctx._section(sec, lang))
        else:
            parts.append(f"[NOT FOUND: '{query}' was not found in the form]")

        return "\n\n===\n\n".join(filter(None, parts))

    # ── Answer building ───────────────────────────────────────────────────────

    def _build_answer(self, user_input: str, context_str: str, intent: str,
                      confusion: Optional[str], cur_move: Optional[str],
                      lang: str, s: Session) -> str:
        """Build final answer and save to session."""
        final_cursor = FormCursor.from_dict(s.cursor)

        if final_cursor.field:         cursor_type = 'field'
        elif final_cursor.field_group: cursor_type = 'field_group'
        elif final_cursor.subsection:  cursor_type = 'subsection'
        elif final_cursor.section:     cursor_type = 'section'
        else:                          cursor_type = None

        explain_input = "Explain this section." if cur_move in ("next", "up") else user_input
        history_for_explain = s.history if intent == INTENT_FOLLOWUP else []

        answer = self._explain(
            explain_input, context_str, lang, intent, confusion,
            self._format_breadcrumb(final_cursor, lang),
            history_for_explain, s.get_user_context_summary(),
            cursor_type=cursor_type
        )

        bc = self._format_breadcrumb(final_cursor, lang)
        if bc:
            answer = f"📍 {bc}\n\n{answer}"

        # Save to history WITHOUT breadcrumb — otherwise LLM reproduces it
        answer_for_history = answer
        if answer.startswith('📍'):
            lines = answer.split('\n')
            answer_for_history = '\n'.join(lines[2:]).strip()

        s.add_turn(user_input, answer_for_history)
        return answer

    # ── Helper: format breadcrumb ─────────────────────────────────────────────

    def _format_breadcrumb(self, cursor: FormCursor, lang: str) -> str:
        parts = []
        if cursor.section and cursor.section in self.fk.sections:
            sec = self.fk.sections[cursor.section]
            parts.append(f"{'Abschnitt' if lang == 'de' else 'Section'} {cursor.section}: {sec.name}")
        if cursor.subsection:
            parts.append(cursor.subsection)
        if cursor.field_group and cursor.field_group != cursor.subsection:
            parts.append(cursor.field_group)
        if cursor.field:
            field_label = cursor.field
            results = self.fk.search(cursor.field, lang, section_filter=cursor.section)
            for r in results:
                if r['type'] == 'field' and r['object'].field_name == cursor.field:
                    field_label = r['object'].field_label
                    break
            parts.append(field_label)
        return " → ".join(parts)

    # ── Helper: format result path ────────────────────────────────────────────

    def _format_result_path(self, r: dict, sec, include_section: bool = True, lang: str = 'en') -> str:
        """Format a search result as a human-readable path."""
        parts = []

        if include_section and sec:
            label = "Abschnitt" if lang == 'de' else "Section"
            parts.append(f"{label} {r['section']}: {sec.name}")

        if r.get('subsection') and sec:
            for parent_sub in sec.subsections:
                if hasattr(parent_sub, 'subsections'):
                    for nested in parent_sub.subsections:
                        if nested.name == r['subsection']:
                            parts.append(parent_sub.name)
                            break

        if r.get('subsection'):
            parts.append(r['subsection'])
        if r.get('field_group') or r.get('group'):
            parts.append(r.get('field_group') or r.get('group'))

        obj = r['object']
        if r['type'] == 'field':
            parts.append(obj.field_label)
        elif r['type'] == 'subsection':
            if not parts or parts[-1] != obj.name:
                parts.append(obj.name)
        elif r['type'] == 'field_group':
            if not parts or parts[-1] != obj.group_name:
                parts.append(obj.group_name)

        return ' → '.join(parts)

    # ── Cursor update ─────────────────────────────────────────────────────────
    def _update_cursor(self, intent, query, cursor, lang):
        if intent == INTENT_FOLLOWUP:
            return cursor.to_dict(), []

        if intent == INTENT_NAVIGATE and query.strip().isdigit():
            sec_num = int(query.strip())
            if sec_num in self.fk.sections:
                sec = self.fk.sections[sec_num]
                nc = FormCursor(section=sec.number)
                opts = ([s.name for s in sec.subsections] +
                        [f.field_label for f in sec.fields] +
                        [fg.group_name for fg in sec.field_groups])
                return nc.to_dict(), opts
            return cursor.to_dict(), []

        q = query.lower().strip()

        def _search_with_fallback(query_str, **kwargs):
            results = self.fk.search(query_str, lang, **kwargs)
            good = [r for r in results if r['score'] >= 30]
            if not good:
                stripped = re.sub(r'\s*\([^)]+\)\s*$', '', query_str).strip()
                if stripped != query_str:
                    results = self.fk.search(stripped, lang, **kwargs)
                    good = [r for r in results if r['score'] >= 30]
            return good

        if cursor.section:
            good = _search_with_fallback(
                query,
                section_filter=cursor.section,
                current_section=cursor.section,
                current_subsection=cursor.subsection,
                current_field_group=cursor.field_group
            )
            stripped_q = re.sub(r'\s*\([^)]+\)\s*$', '', query).strip().lower()
            if stripped_q != q and good:
                q = stripped_q

            if good:
                # Case 0: on a field — look for sibling/parent matches first
                if cursor.field:
                    candidates = [r for r in good
                                if r['type'] in ('subsection', 'field', 'field_group')
                                and r['object'] != cursor.field]
                    exact_up = [r for r in candidates if (
                                (r['type'] == 'subsection' and r['object'].name.lower() == q) or
                                (r['type'] == 'field' and r['object'].field_label.lower() == q) or
                                (r['type'] == 'field_group' and r['object'].group_name.lower() == q))]
                    if len(exact_up) == 1:
                        return self._make_cursor_from_result(exact_up[0], cursor), []

                # Case 1: in subsection — search inside it
                if cursor.subsection and not cursor.field_group:
                    exact_in_sub = [r for r in good
                                    if r.get('subsection') == cursor.subsection
                                    and r['type'] in ('field', 'field_group')
                                    and (
                                        (r['type'] == 'field' and r['object'].field_label.lower() == q) or
                                        (r['type'] == 'field_group' and r['object'].group_name.lower() == q)
                                    )]
                    if len(exact_in_sub) == 1:
                        return self._make_cursor_from_result(exact_in_sub[0], cursor), []

                    good_in_sub = [r for r in good
                                if r.get('subsection') == cursor.subsection
                                and r['type'] in ('field', 'field_group')
                                and r['score'] >= 50]
                    print(f"[DEBUG GIS] good_in_sub count={len(good_in_sub)}")
                    for r in good_in_sub:
                        print(f"  score={r['score']} name={r['object'].field_label}")
                    if len(good_in_sub) == 1:
                        return self._make_cursor_from_result(good_in_sub[0], cursor), []

                    if len(good_in_sub) > 1:
                        # Prefer field_group over its fields if both match
                        fgs = [r for r in good_in_sub if r['type'] == 'field_group']
                        fields_in_fg = [r for r in good_in_sub
                                        if r['type'] == 'field'
                                        and r.get('group') in {fg['object'].group_name for fg in fgs}]
                        if len(fgs) == 1 and len(fields_in_fg) == len(good_in_sub) - 1:
                            return self._make_cursor_from_result(fgs[0], cursor), []
                        return {'ambiguous': True, 'options': good_in_sub, 'cursor': cursor.to_dict()}, []

                # Case 2: in field_group — search inside it
                if cursor.field_group and not cursor.field:
                    if q == cursor.field_group.lower():
                        fg_obj = self.fk.get_field_group(cursor.section, cursor.subsection, cursor.field_group)
                        if fg_obj:
                            matching = next((f for f in fg_obj.fields if f.field_label.lower() == q), None)
                            if matching:
                                return FormCursor(
                                    section=cursor.section,
                                    subsection=cursor.subsection,
                                    field_group=cursor.field_group,
                                    field=matching.field_name
                                ).to_dict(), []

                    exact_in_fg = [r for r in good
                                   if r.get('group') == cursor.field_group
                                   and r['type'] == 'field'
                                   and r['object'].field_label.lower() == q]
                    if len(exact_in_fg) == 1:
                        return self._make_cursor_from_result(exact_in_fg[0], cursor), []

                    starts_in_fg = [r for r in good
                                    if r.get('group') == cursor.field_group
                                    and r['type'] == 'field'
                                    and r['object'].field_label.lower().startswith(q)]
                    if len(starts_in_fg) == 1:
                        return self._make_cursor_from_result(starts_in_fg[0], cursor), []

                # Case 3: at section root — exact subsection match
                if not cursor.subsection:
                    exact_subs = [r for r in good
                                if r['type'] == 'subsection'
                                and r['object'].name.lower() == q]
                    if len(exact_subs) == 1:
                        return self._make_cursor_from_result(exact_subs[0], cursor), []

                # Case 4: in subsection — field with same name as subsection
                if cursor.subsection and not cursor.field_group:
                    exact_fields = [r for r in good
                                    if r['type'] == 'field'
                                    and r.get('subsection') == cursor.subsection
                                    and r['object'].field_label.lower() == q]
                    if len(exact_fields) == 1:
                        return self._make_cursor_from_result(exact_fields[0], cursor), []

                # Case 5: at section root — direct children only
                if not cursor.subsection and not cursor.field_group:
                    sec_obj = self.fk.get_section(cursor.section)
                    if sec_obj:
                        direct_sub_names = {sub.name.lower() for sub in sec_obj.subsections}
                        direct_field_names = {f.field_label.lower() for f in sec_obj.fields}
                        direct_fg_names = {fg.group_name.lower() for fg in sec_obj.field_groups}
                        direct_children = [
                            r for r in good
                            if (r['type'] == 'subsection' and r['object'].name.lower() in direct_sub_names)
                            or (r['type'] == 'field' and r['object'].field_label.lower() in direct_field_names)
                            or (r['type'] == 'field_group' and r['object'].group_name.lower() in direct_fg_names)
                        ]
                        if len(direct_children) == 1:
                            return self._make_cursor_from_result(direct_children[0], cursor), []
                        if len(direct_children) > 1 and len(q) >= 5:
                            startswith_match = [
                                r for r in direct_children
                                if (r['type'] == 'field' and r['object'].field_label.lower().startswith(q))
                                or (r['type'] == 'subsection' and r['object'].name.lower().startswith(q))
                                or (r['type'] == 'field_group' and r['object'].group_name.lower().startswith(q))
                            ]
                            if len(startswith_match) == 1:
                                return self._make_cursor_from_result(startswith_match[0], cursor), []

                # Standard exact match check
                exact = None
                for r in good:
                    obj = r['object']
                    name = (obj.name.lower() if r['type'] in ('section', 'subsection') else
                            obj.group_name.lower() if r['type'] == 'field_group' else
                            obj.field_label.lower() if r['type'] == 'field' else '')
                    if q == name:
                        exact = r
                        break

                if exact:
                    all_exact = [r for r in good if (
                        (r['type'] == 'field' and r['object'].field_label.lower() == q) or
                        (r['type'] == 'subsection' and r['object'].name.lower() == q) or
                        (r['type'] == 'field_group' and r['object'].group_name.lower() == q) or
                        (r['type'] == 'section' and r['object'].name.lower() == q)
                    )]
                    if len(all_exact) == 1:
                        return self._make_cursor_from_result(exact, cursor), []
                    return {'ambiguous': True, 'options': all_exact, 'cursor': cursor.to_dict()}, []

                if len(good) == 1:
                    return self._make_cursor_from_result(good[0], cursor), []

                return {'ambiguous': True, 'options': good, 'cursor': cursor.to_dict()}, []

        # Search everywhere
        all_results = self.fk.search(query, lang)
        good_all = [r for r in all_results if r['score'] >= 40]

        if not good_all:
            return cursor.to_dict(), []

        for r in good_all:
            obj = r['object']
            name = (obj.name.lower() if r['type'] in ('section', 'subsection') else
                    obj.group_name.lower() if r['type'] == 'field_group' else
                    obj.field_label.lower() if r['type'] == 'field' else '')
            if q == name or (len(q) >= 5 and name.startswith(q)):
                return self._make_cursor_from_result(r, cursor), []

        if len(good_all) == 1:
            return self._make_cursor_from_result(good_all[0], cursor), []

        seen = set()
        deduped = []
        for r in good_all:
            obj = r['object']
            if r['type'] == 'field':
                key = (r['section'], r.get('subsection'), r.get('group'), obj.field_name)
            elif r['type'] == 'field_group':
                key = (r['section'], r.get('subsection'), obj.group_name)
            elif r['type'] == 'subsection':
                key = (r['section'], obj.name)
            else:
                key = (r['section'], r['type'])
            if key not in seen:
                seen.add(key)
                deduped.append(r)

        if len(deduped) == 1:
            return self._make_cursor_from_result(deduped[0], cursor), []

        return {'ambiguous': True, 'options': deduped, 'cursor': cursor.to_dict()}, []

    # ── Make cursor from search result ────────────────────────────────────────

    def _make_cursor_from_result(self, r: dict, old_cursor: FormCursor) -> dict:
        typ = r['type']

        def find_parent_sub(section_num, sub_name):
            sec = self.fk.get_section(section_num)
            if not sec:
                return None
            for parent in sec.subsections:
                if hasattr(parent, 'subsections'):
                    for nested in parent.subsections:
                        if nested.name == sub_name:
                            return parent.name
            return None

        if typ == 'section':
            return FormCursor(section=r['object'].number).to_dict()

        if typ == 'subsection':
            sub = r['object']
            parent = find_parent_sub(r['section'], sub.name)
            return FormCursor(section=r['section'], parent_subsection=parent, subsection=sub.name).to_dict()

        if typ == 'field_group':
            fg = r['object']
            parent = find_parent_sub(r['section'], r.get('subsection')) if r.get('subsection') else None
            return FormCursor(section=r['section'], parent_subsection=parent,
                              subsection=r.get('subsection'), field_group=fg.group_name).to_dict()

        if typ == 'field':
            f = r['object']
            parent = find_parent_sub(r['section'], r.get('subsection')) if r.get('subsection') else None
            field_group = (r.get('field_group') or r.get('group') or
                           (f.group_path[-1] if f.group_path else None))
            return FormCursor(section=r['section'], parent_subsection=parent,
                              subsection=r.get('subsection'), field_group=field_group,
                              field=f.field_name).to_dict()

        return old_cursor.to_dict()

    # ── Explain ───────────────────────────────────────────────────────────────

    def _explain(self, user_input, context, lang, intent, confusion,
                 cursor_bc, history, user_context_summary="", cursor_type=None) -> str:
        # follow_up — lightweight prompt with conversation history only
        if intent == INTENT_FOLLOWUP:
            position_hint = f"[Context: user is currently filling out {cursor_bc}]" if cursor_bc and cursor_bc != 'root' else ""
            user_ctx_hint = f"[User info: {user_context_summary}]" if user_context_summary else ""
            nav_tip = ("🧭 Zur Navigation geben Sie eine Abschnittsnummer oder den DEUTSCHEN Namen eines Abschnitts, Unterabschnitts oder Feldes ein – z.B. '7', 'Kleinunternehmer-Regelung' oder 'Geburtsdatum'."
                    if lang == 'de' else
                    "🧭 To navigate the form, type a section number or the GERMAN name of a section, subsection, or field — e.g. '7', 'Kleinunternehmer-Regelung', or 'Geburtsdatum'.")
            lang_system = FOLLOWUP_SYSTEM + f"\n\nIMPORTANT: Always respond in {'German' if lang == 'de' else 'English'}, regardless of the language the user writes in. Always end with exactly: {nav_tip}"
            user_msg = "\n\n".join(filter(None, [position_hint, user_ctx_hint, user_input]))
            messages = list(history) + [{"role": "user", "content": user_msg}]
            return self.llm.complete(
                messages=messages,
                system=lang_system,
                max_tokens=300,
                temperature=0.5
            )

        # All other intents — EXPLAIN_SYSTEM with form context
        parts = []
        if user_context_summary:
            parts.append(user_context_summary)
        if context:
            parts.append(f"[FORM CONTEXT]\n{context}")
        if cursor_bc and cursor_bc != 'root':
            parts.append(f"[CURRENT POSITION: {cursor_bc}]")
        if cursor_type:
            parts.append(f"[CURRENT LOCATION TYPE: {cursor_type}]")
        if confusion:
            hints = {
                "umsatz_gewinn":    "Note: user confuses Umsatz (revenue) and Gewinn (profit).",
                "steuernummer_ust": "Note: user confuses Steuernummer and USt-IdNr.",
                "estimate_vs_fact": "Note: user treats estimate fields as exact values.",
            }
            if confusion in hints:
                parts.append(hints[confusion])

        parts.append("Answer in German." if lang == 'de'
                     else "Answer in English. Keep German form terms in German.")
        parts.append(f"\nUser question: {user_input}")

        full_msg = "\n\n".join(filter(None, parts))
        messages = [{"role": "user", "content": full_msg}]

        return self.llm.complete(messages=messages, system=EXPLAIN_SYSTEM,
                                 max_tokens=1500, temperature=0.3)
