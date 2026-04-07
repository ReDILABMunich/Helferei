import re

# ─────────────────────────────────────────────────────────────────────────────
# GLOSSARY
# ─────────────────────────────────────────────────────────────────────────────

GLOSSARY = {

    "kleinunternehmer": {
        "term_de": "Kleinunternehmerregelung (§19 UStG)",
        "term_en": "Small business VAT exemption",
        "definition_de": (
            "Wenn Ihr Jahresumsatz unter 22.000 EUR liegt, können Sie die "
            "Kleinunternehmerregelung nutzen: keine Umsatzsteuer auf Rechnungen, "
            "keine USt-Voranmeldung.\n\n"
            "Vorteile: einfachere Buchführung, keine USt-Ausweis\n"
            "Nachteil: kein Vorsteuerabzug möglich"
        ),
        "definition_en": (
            "If your annual revenue is below EUR 22,000, you can use the small "
            "business exemption: no VAT on invoices, no VAT returns.\n\n"
            "Advantages: simpler bookkeeping, no VAT shown\n"
            "Disadvantage: cannot reclaim input VAT"
        ),
        "keywords": ["kleinunternehmer", "small business", "§19", "vat exemption"],
        "related_sections": [18],
    },
    
    "eur": {
        "term_de": "Einnahmen-Überschuss-Rechnung (EÜR)",
        "term_en": "EÜR - simplified profit calculation",
        "definition_de": (
            "Die EÜR ist die einfachste Gewinnermittlung: Einnahmen minus Ausgaben = Gewinn.\n"
            "Keine doppelte Buchführung erforderlich.\n\n"
            "Gilt für: alle Freiberufler; Gewerbetreibende bis ca. 60.000 EUR Gewinn"
        ),
        "definition_en": (
            "EÜR is the simplified profit method: income minus expenses = profit.\n"
            "No double-entry bookkeeping required.\n\n"
            "For: all freelancers; traders below ~EUR 60k profit"
        ),
        "keywords": ["eur", "eür", "einnahmen überschuss", "gewinnermittlung"],
        "related_sections": [15],
    },
    
    "umsatz_gewinn": {
        "term_de": "Umsatz vs Gewinn",
        "term_en": "Revenue vs Profit",
        "definition_de": (
            "Umsatz = alle Einnahmen VOR Abzug von Kosten\n"
            "Gewinn = Umsatz MINUS Betriebsausgaben\n\n"
            "Wichtig: Das Formular fragt nach UMSATZ, nicht Gewinn!"
        ),
        "definition_en": (
            "Umsatz (revenue) = all income BEFORE expenses\n"
            "Gewinn (profit) = revenue MINUS expenses\n\n"
            "Important: The form asks for UMSATZ (revenue), not profit!"
        ),
        "keywords": ["umsatz", "gewinn", "revenue", "profit"],
        "related_sections": [14, 22],
    },
    
    "vorsteuer": {
        "term_de": "Vorsteuer",
        "term_en": "Input VAT",
        "definition_de": (
            "Vorsteuer ist die USt auf Ihre Einkäufe, die Sie vom Finanzamt "
            "zurückfordern können.\n\n"
            "Nur möglich wenn Sie NICHT Kleinunternehmer sind."
        ),
        "definition_en": (
            "Input VAT is the VAT on your purchases that you can reclaim.\n\n"
            "Only possible if you're NOT using Kleinunternehmer exemption."
        ),
        "keywords": ["vorsteuer", "input vat", "vat reclaim"],
        "related_sections": [18],
    },
    
    "steuernummer": {
        "term_de": "Steuernummer vs USt-IdNr.",
        "term_en": "Tax number vs VAT ID",
        "definition_de": (
            "Steuernummer: Ihre deutsche Nummer beim Finanzamt\n"
            "USt-IdNr.: EU-weite Nummer (Format: DE + 9 Ziffern)\n\n"
            "Das sind ZWEI verschiedene Nummern!"
        ),
        "definition_en": (
            "Steuernummer: your German tax number\n"
            "USt-IdNr. (VAT ID): EU-wide number (DE + 9 digits)\n\n"
            "These are TWO different numbers!"
        ),
        "keywords": ["steuernummer", "ust-idnr", "vat id", "tax number"],
        "related_sections": [1, 6],
    },
    
    "freiberufler": {
        "term_de": "Freiberufler",
        "term_en": "Freelancer (liberal profession)",
        "definition_de": (
            "Freiberufler: Ärzte, Anwälte, Ingenieure, Künstler, IT-Berater.\n\n"
            "Vorteil: keine Gewerbesteuer, keine Gewerbeanmeldung"
        ),
        "definition_en": (
            "Freiberufler: doctors, lawyers, engineers, artists, IT consultants.\n\n"
            "Advantage: no trade tax, no trade registration required"
        ),
        "keywords": ["freiberufler", "freelancer", "liberal profession"],
        "related_sections": [7, 8],
    },
    
    "betriebsstatte": {
        "term_de": "Betriebsstätte",
        "term_en": "Place of business",
        "definition_de": (
            "Betriebsstätte: fester Ort der Tätigkeit\n"
            "Ort der Geschäftsleitung: wo Entscheidungen getroffen werden\n\n"
            "Bei Einzelunternehmern meist identisch mit Wohnadresse."
        ),
        "definition_en": (
            "Betriebsstätte: fixed place of business\n"
            "Management seat: where decisions are made\n\n"
            "For sole traders, usually same as home address."
        ),
        "keywords": ["betriebsstatte", "betriebsstaette", "place of business"],
        "related_sections": [6],
    },

    "gewerbesteuer": {
        "term_de": "Gewerbesteuer",
        "term_en": "Trade tax",
        "definition_de": (
            "Kommunale Steuer für Gewerbetreibende (nicht Freiberufler).\n"
            "Freibetrag: 24.500 EUR pro Jahr.\n\n"
            "Hebesatz variiert je nach Gemeinde (7-17% vom Gewerbeertrag)."
        ),
        "definition_en": (
            "Municipal tax for traders (not freelancers).\n"
            "Allowance: EUR 24,500 per year.\n\n"
            "Rate varies by municipality (7-17% of trade income)."
        ),
        "keywords": ["gewerbesteuer", "trade tax", "municipal tax", "hebesatz"],
        "related_sections": [7],
    },
    
    "einkommensteuer": {
        "term_de": "Einkommensteuer",
        "term_en": "Income tax",
        "definition_de": (
            "Persönliche Steuer auf Ihr Einkommen.\n"
            "Progressiver Steuersatz: 0% bis 45% (Grundfreibetrag: ~11.000 EUR).\n\n"
            "Gilt für Gewinne aus selbständiger und nicht-selbständiger Arbeit."
        ),
        "definition_en": (
            "Personal tax on your income.\n"
            "Progressive rate: 0% to 45% (tax-free allowance: ~EUR 11,000).\n\n"
            "Applies to profits from self-employed and employed work."
        ),
        "keywords": ["einkommensteuer", "income tax", "est"],
        "related_sections": [14, 22],
    },
    
    "umsatzsteuer": {
        "term_de": "Umsatzsteuer (USt)",
        "term_en": "Value Added Tax (VAT)",
        "definition_de": (
            "Steuer auf Verkäufe: Regelsteuersatz 19%, ermäßigt 7%.\n"
            "Sie ziehen diese ein und führen sie ans Finanzamt ab.\n\n"
            "Ausnahme: Kleinunternehmer (§19 UStG) müssen keine USt erheben."
        ),
        "definition_en": (
            "Tax on sales: standard rate 19%, reduced 7%.\n"
            "You collect it and pay to tax office.\n\n"
            "Exception: Small businesses (§19) don't charge VAT."
        ),
        "keywords": ["umsatzsteuer", "ust", "vat", "mehrwertsteuer"],
        "related_sections": [18, 19, 20, 21],
    },
    
    "vorauszahlung": {
        "term_de": "Vorauszahlung",
        "term_en": "Advance tax payment",
        "definition_de": (
            "Vierteljährliche Vorauszahlungen auf Einkommen- und Gewerbesteuer.\n"
            "Basiert auf geschätztem Gewinn.\n\n"
            "Wird bei der Jahressteuererklärung verrechnet."
        ),
        "definition_en": (
            "Quarterly advance payments for income and trade tax.\n"
            "Based on estimated profit.\n\n"
            "Offset against annual tax return."
        ),
        "keywords": ["vorauszahlung", "advance payment", "quarterly payment"],
        "related_sections": [22],
    },
    
    "solidaritatszuschlag": {
        "term_de": "Solidaritätszuschlag",
        "term_en": "Solidarity surcharge",
        "definition_de": (
            "Zuschlag zur Einkommensteuer: 5,5% der Einkommensteuer.\n"
            "Seit 2021 für die meisten abgeschafft (nur Spitzenverdiener)."
        ),
        "definition_en": (
            "Surcharge on income tax: 5.5% of income tax.\n"
            "Abolished for most since 2021 (only high earners)."
        ),
        "keywords": ["solidaritätszuschlag", "soli", "solidarity surcharge"],
        "related_sections": [22],
    },
    
    "kirchensteuer": {
        "term_de": "Kirchensteuer",
        "term_en": "Church tax",
        "definition_de": (
            "Steuer für Kirchenmitglieder: 8-9% der Einkommensteuer.\n"
            "Variiert je nach Bundesland.\n\n"
            "Wird automatisch abgezogen wenn Sie Kirchenmitglied sind."
        ),
        "definition_en": (
            "Tax for church members: 8-9% of income tax.\n"
            "Varies by state.\n\n"
            "Automatically deducted if you're a church member."
        ),
        "keywords": ["kirchensteuer", "church tax"],
        "related_sections": [1],
    },
    
    "lohnsteuer": {
        "term_de": "Lohnsteuer",
        "term_en": "Payroll tax",
        "definition_de": (
            "Einkommensteuer für Angestellte, vom Arbeitgeber einbehalten.\n"
            "Als Selbständiger zahlen Sie Einkommensteuer, nicht Lohnsteuer."
        ),
        "definition_en": (
            "Income tax for employees, withheld by employer.\n"
            "As self-employed, you pay income tax, not payroll tax."
        ),
        "keywords": ["lohnsteuer", "payroll tax", "wage tax"],
        "related_sections": [],
    },
    
    "ist_versteuerung": {
        "term_de": "Ist-Versteuerung",
        "term_en": "Cash-basis VAT accounting",
        "definition_de": (
            "USt wird erst bei Zahlungseingang fällig.\n"
            "Vorteil: bessere Liquidität.\n\n"
            "Berechtigt bis 600.000 EUR Umsatz im Vorjahr."
        ),
        "definition_en": (
            "VAT due only when payment received.\n"
            "Advantage: better cash flow.\n\n"
            "Eligible up to EUR 600k revenue in previous year."
        ),
        "keywords": ["ist-versteuerung", "ist versteuerung", "cash basis vat"],
        "related_sections": [18],
    },
    
    "soll_versteuerung": {
        "term_de": "Soll-Versteuerung",
        "term_en": "Invoice-basis VAT accounting",
        "definition_de": (
            "USt wird bei Rechnungsstellung fällig (auch wenn nicht bezahlt).\n"
            "Standard-Methode für größere Unternehmen.\n\n"
            "Pflicht ab 600.000 EUR Umsatz."
        ),
        "definition_en": (
            "VAT due when invoice issued (even if unpaid).\n"
            "Standard method for larger businesses.\n\n"
            "Mandatory above EUR 600k revenue."
        ),
        "keywords": ["soll-versteuerung", "soll versteuerung", "invoice basis vat"],
        "related_sections": [18],
    },
    
    "dauerfristverlangerung": {
        "term_de": "Dauerfristverlängerung",
        "term_en": "Permanent deadline extension (VAT)",
        "definition_de": (
            "Verlängert die Abgabefrist für USt-Voranmeldung um 1 Monat.\n"
            "Erfordert 1/11 Sondervorauszahlung.\n\n"
            "Muss beim Finanzamt beantragt werden."
        ),
        "definition_en": (
            "Extends VAT return deadline by 1 month.\n"
            "Requires 1/11 special advance payment.\n\n"
            "Must be applied for at tax office."
        ),
        "keywords": ["dauerfristverlängerung", "deadline extension", "fristverlängerung"],
        "related_sections": [18],
    },
    
    "vorsteuerabzug": {
        "term_de": "Vorsteuerabzug",
        "term_en": "Input VAT deduction",
        "definition_de": (
            "Recht, die auf Einkäufe gezahlte USt vom Finanzamt zurückzufordern.\n"
            "Nur möglich wenn Sie USt-pflichtig sind (nicht Kleinunternehmer)."
        ),
        "definition_en": (
            "Right to reclaim VAT paid on purchases from tax office.\n"
            "Only possible if you charge VAT (not small business exemption)."
        ),
        "keywords": ["vorsteuerabzug", "input vat deduction", "vat deduction"],
        "related_sections": [18],
    },
    
    "reverse_charge": {
        "term_de": "Reverse-Charge-Verfahren",
        "term_en": "Reverse charge mechanism",
        "definition_de": (
            "Bei B2B-Dienstleistungen ins EU-Ausland schuldet der EMPFÄNGER die USt.\n"
            "Sie stellen Rechnung ohne deutsche USt.\n\n"
            "Wichtig: Prüfung der USt-IdNr. des Empfängers erforderlich."
        ),
        "definition_en": (
            "For B2B services to EU abroad, RECIPIENT owes VAT.\n"
            "You invoice without German VAT.\n\n"
            "Important: Must verify recipient's VAT ID."
        ),
        "keywords": ["reverse charge", "reverse-charge", "umkehr der steuerschuldnerschaft"],
        "related_sections": [19],
    },
    
    "umsatzsteuer_voranmeldung": {
        "term_de": "Umsatzsteuer-Voranmeldung",
        "term_en": "VAT advance return",
        "definition_de": (
            "Monatliche oder vierteljährliche Meldung der USt ans Finanzamt.\n"
            "Frist: bis 10. des Folgemonats (bei ELSTER: 10 Tage später).\n\n"
            "Im ersten und zweiten Jahr: monatlich. Danach: vierteljährlich wenn USt < 7.500 EUR."
        ),
        "definition_en": (
            "Monthly or quarterly VAT report to tax office.\n"
            "Deadline: 10th of following month (ELSTER: 10 days later).\n\n"
            "First 2 years: monthly. Then: quarterly if VAT < EUR 7,500."
        ),
        "keywords": ["ust-voranmeldung", "vat return", "advance vat return"],
        "related_sections": [18],
    },
    
    "umsatzsteuerjahreserklarung": {
        "term_de": "Umsatzsteuerjahreserklärung",
        "term_en": "Annual VAT return",
        "definition_de": (
            "Jährliche Zusammenfassung aller USt-Voranmeldungen.\n"
            "Frist: 31. Juli des Folgejahres (mit Steuerberater: länger).\n\n"
            "Pflicht für alle USt-Pflichtigen (außer Kleinunternehmer)."
        ),
        "definition_en": (
            "Annual summary of all VAT advance returns.\n"
            "Deadline: July 31 of following year (with tax advisor: longer).\n\n"
            "Mandatory for all VAT-liable businesses (except small businesses)."
        ),
        "keywords": ["umsatzsteuerjahreserklärung", "annual vat return"],
        "related_sections": [18],
    },
    
    "umsatzsteuer_identifikationsnummer": {
        "term_de": "Umsatzsteuer-Identifikationsnummer (USt-IdNr.)",
        "term_en": "VAT identification number",
        "definition_de": (
            "EU-weite Nummer für grenzüberschreitende Geschäfte: DE + 9 Ziffern.\n"
            "Beantragung: beim Bundeszentralamt für Steuern.\n\n"
            "Pflicht für innergemeinschaftliche Lieferungen."
        ),
        "definition_en": (
            "EU-wide number for cross-border business: DE + 9 digits.\n"
            "Application: Federal Central Tax Office.\n\n"
            "Required for intra-community supplies."
        ),
        "keywords": ["ust-idnr", "vat id", "vat identification number", "ustid"],
        "related_sections": [6, 19],
    },
 
    "einzelunternehmen": {
        "term_de": "Einzelunternehmen",
        "term_en": "Sole proprietorship",
        "definition_de": (
            "Einfachste Unternehmensform: eine Person führt das Unternehmen.\n"
            "Unbeschränkte persönliche Haftung.\n\n"
            "Keine Mindestkapital erforderlich. Gewinn ist Ihr persönliches Einkommen."
        ),
        "definition_en": (
            "Simplest business form: one person runs the business.\n"
            "Unlimited personal liability.\n\n"
            "No minimum capital required. Profit is your personal income."
        ),
        "keywords": ["einzelunternehmen", "sole proprietorship", "einzelunternehmer"],
        "related_sections": [1, 7],
    },
    
    "gewerbetreibender": {
        "term_de": "Gewerbetreibender",
        "term_en": "Trader / Commercial business",
        "definition_de": (
            "Unternehmer der ein Gewerbe ausübt (im Gegensatz zu Freiberufler).\n"
            "Muss Gewerbesteuer zahlen.\n\n"
            "Beispiele: Händler, Handwerker, Online-Shops, Gastronomen."
        ),
        "definition_en": (
            "Entrepreneur running a commercial business (vs freelancer).\n"
            "Must pay trade tax.\n\n"
            "Examples: traders, craftsmen, online shops, restaurants."
        ),
        "keywords": ["gewerbetreibender", "trader", "commercial business", "gewerbe"],
        "related_sections": [7, 8],
    },
    
    "personengesellschaft": {
        "term_de": "Personengesellschaft",
        "term_en": "Partnership",
        "definition_de": (
            "Zusammenschluss von mindestens 2 Personen: GbR, OHG, KG.\n"
            "Gesellschafter haften persönlich (außer Kommanditisten bei KG)."
        ),
        "definition_en": (
            "Partnership of at least 2 persons: GbR, OHG, KG.\n"
            "Partners liable personally (except limited partners in KG)."
        ),
        "keywords": ["personengesellschaft", "partnership", "gbr", "ohg", "kg"],
        "related_sections": [],
    },
    
    "kapitalgesellschaft": {
        "term_de": "Kapitalgesellschaft",
        "term_en": "Corporation",
        "definition_de": (
            "Juristische Person: GmbH, UG, AG.\n"
            "Haftung beschränkt auf Gesellschaftsvermögen.\n\n"
            "Mindestkapital: GmbH 25.000 EUR, UG 1 EUR, AG 50.000 EUR."
        ),
        "definition_en": (
            "Legal entity: GmbH, UG, AG.\n"
            "Liability limited to company assets.\n\n"
            "Minimum capital: GmbH EUR 25k, UG EUR 1, AG EUR 50k."
        ),
        "keywords": ["kapitalgesellschaft", "corporation", "gmbh", "ug", "ag"],
        "related_sections": [],
    },
    
    "gbr": {
        "term_de": "Gesellschaft bürgerlichen Rechts (GbR)",
        "term_en": "Civil law partnership",
        "definition_de": (
            "Einfachste Partnerschaft: ab 2 Personen.\n"
            "Alle Gesellschafter haften unbeschränkt.\n\n"
            "Keine Registrierung im Handelsregister erforderlich."
        ),
        "definition_en": (
            "Simplest partnership: from 2 persons.\n"
            "All partners have unlimited liability.\n\n"
            "No commercial register entry required."
        ),
        "keywords": ["gbr", "gesellschaft bürgerlichen rechts", "civil partnership"],
        "related_sections": [],
    },
    
    "gmbh": {
        "term_de": "Gesellschaft mit beschränkter Haftung (GmbH)",
        "term_en": "Limited liability company",
        "definition_de": (
            "Haftung beschränkt auf Gesellschaftsvermögen.\n"
            "Mindestkapital: 25.000 EUR.\n\n"
            "Unterliegt Körperschaftsteuer (15%) statt Einkommensteuer."
        ),
        "definition_en": (
            "Liability limited to company assets.\n"
            "Minimum capital: EUR 25,000.\n\n"
            "Subject to corporate tax (15%) instead of income tax."
        ),
        "keywords": ["gmbh", "limited liability company", "gesellschaft mit beschränkter haftung"],
        "related_sections": [],
    },
    
    "ug": {
        "term_de": "Unternehmergesellschaft (UG)",
        "term_en": "Mini-GmbH",
        "definition_de": (
            "Variante der GmbH mit geringerem Startkapital (ab 1 EUR).\n"
            "Muss Rücklagen bilden bis 25.000 EUR erreicht sind.\n\n"
            "Dann Umwandlung in GmbH möglich."
        ),
        "definition_en": (
            "GmbH variant with lower start capital (from EUR 1).\n"
            "Must build reserves until EUR 25k reached.\n\n"
            "Then conversion to GmbH possible."
        ),
        "keywords": ["ug", "unternehmergesellschaft", "mini-gmbh"],
        "related_sections": [],
    },
    
    "natürliche_person": {
        "term_de": "Natürliche Person",
        "term_en": "Natural person",
        "definition_de": (
            "Sie als Mensch (im Gegensatz zu juristischen Personen wie GmbH).\n"
            "Als Einzelunternehmer sind Sie eine natürliche Person."
        ),
        "definition_en": (
            "You as a human being (vs legal entities like GmbH).\n"
            "As sole proprietor, you are a natural person."
        ),
        "keywords": ["natürliche person", "natural person"],
        "related_sections": [6],
    },
    
    "juristische_person": {
        "term_de": "Juristische Person",
        "term_en": "Legal entity",
        "definition_de": (
            "Rechtlich eigenständige Einheit: GmbH, AG, Verein.\n"
            "Hat eigene Rechte und Pflichten, unabhängig von Gesellschaftern."
        ),
        "definition_en": (
            "Legally independent entity: GmbH, AG, association.\n"
            "Has own rights and obligations, independent of shareholders."
        ),
        "keywords": ["juristische person", "legal entity", "legal person"],
        "related_sections": [],
    },
    
    "kaufmann": {
        "term_de": "Kaufmann",
        "term_en": "Merchant",
        "definition_de": (
            "Gewerbetreibender der im Handelsregister eingetragen ist.\n"
            "Pflicht bei Umsatz > ~600.000 EUR oder komplexem Geschäft.\n\n"
            "Unterliegt HGB (Handelsgesetzbuch) statt BGB."
        ),
        "definition_en": (
            "Trader registered in commercial register.\n"
            "Required above ~EUR 600k revenue or complex business.\n\n"
            "Subject to Commercial Code instead of Civil Code."
        ),
        "keywords": ["kaufmann", "merchant", "handelsregister"],
        "related_sections": [],
    },
    
    "bilanz": {
        "term_de": "Bilanz",
        "term_en": "Balance sheet",
        "definition_de": (
            "Aufstellung von Vermögen und Schulden zum Jahresende.\n"
            "Erforderlich bei doppelter Buchführung.\n\n"
            "Pflicht für Kaufleute und ab ~600.000 EUR Umsatz."
        ),
        "definition_en": (
            "Statement of assets and liabilities at year-end.\n"
            "Required for double-entry bookkeeping.\n\n"
            "Mandatory for merchants and above ~EUR 600k revenue."
        ),
        "keywords": ["bilanz", "balance sheet", "jahresabschluss"],
        "related_sections": [15],
    },
    
    "doppelte_buchführung": {
        "term_de": "Doppelte Buchführung",
        "term_en": "Double-entry bookkeeping",
        "definition_de": (
            "Jede Buchung wird zweimal erfasst (Soll und Haben).\n"
            "Pflicht für Kaufleute und größere Unternehmen.\n\n"
            "Komplex, meist mit Steuerberater."
        ),
        "definition_en": (
            "Each transaction recorded twice (debit and credit).\n"
            "Required for merchants and larger businesses.\n\n"
            "Complex, usually with tax advisor."
        ),
        "keywords": ["doppelte buchführung", "double-entry bookkeeping", "doppik"],
        "related_sections": [15],
    },
    
    "betriebsausgaben": {
        "term_de": "Betriebsausgaben",
        "term_en": "Business expenses",
        "definition_de": (
            "Alle Kosten die durch Ihre Tätigkeit entstehen.\n"
            "Reduzieren Ihren steuerpflichtigen Gewinn.\n\n"
            "Beispiele: Miete Büro, Software, Fahrtkosten, Weiterbildung."
        ),
        "definition_en": (
            "All costs arising from your business.\n"
            "Reduce your taxable profit.\n\n"
            "Examples: office rent, software, travel costs, training."
        ),
        "keywords": ["betriebsausgaben", "business expenses", "ausgaben", "expenses"],
        "related_sections": [14],
    },
    
    "betriebseinnahmen": {
        "term_de": "Betriebseinnahmen",
        "term_en": "Business income",
        "definition_de": (
            "Alle Einnahmen aus Ihrer selbständigen Tätigkeit.\n"
            "Basis für Umsatzsteuer und Gewinnermittlung.\n\n"
            "Auch Sachleistungen und Tausch zählen als Einnahmen."
        ),
        "definition_en": (
            "All income from your self-employed activity.\n"
            "Basis for VAT and profit calculation.\n\n"
            "In-kind benefits and barter also count as income."
        ),
        "keywords": ["betriebseinnahmen", "business income", "einnahmen", "revenue"],
        "related_sections": [14],
    },
    
    "afa": {
        "term_de": "Absetzung für Abnutzung (AfA)",
        "term_en": "Depreciation",
        "definition_de": (
            "Verteilung der Anschaffungskosten großer Investitionen über mehrere Jahre.\n"
            "Beispiel: Computer (3 Jahre), PKW (6 Jahre), Gebäude (50 Jahre).\n\n"
            "Geringwertige Wirtschaftsgüter (< 800 EUR): sofort absetzbar."
        ),
        "definition_en": (
            "Spreading acquisition costs of large investments over years.\n"
            "Example: computer (3 years), car (6 years), building (50 years).\n\n"
            "Low-value assets (< EUR 800): immediately deductible."
        ),
        "keywords": ["afa", "abschreibung", "depreciation", "absetzung für abnutzung"],
        "related_sections": [14],
    },
    
    "geringwertige_wirtschaftsgüter": {
        "term_de": "Geringwertige Wirtschaftsgüter (GWG)",
        "term_en": "Low-value assets",
        "definition_de": (
            "Anschaffungen bis 800 EUR (netto) können sofort abgeschrieben werden.\n"
            "Keine Verteilung über mehrere Jahre nötig.\n\n"
            "Beispiele: Laptop, Drucker, Schreibtisch."
        ),
        "definition_en": (
            "Purchases up to EUR 800 (net) can be immediately written off.\n"
            "No need to spread over years.\n\n"
            "Examples: laptop, printer, desk."
        ),
        "keywords": ["gwg", "geringwertige wirtschaftsgüter", "low-value assets"],
        "related_sections": [14],
    },
    
    "anlaufverlust": {
        "term_de": "Anlaufverlust",
        "term_en": "Start-up losses",
        "definition_de": (
            "Verluste in den ersten Jahren der Geschäftstätigkeit.\n"
            "Können mit Gewinnen späterer Jahre verrechnet werden (Verlustvortrag)."
        ),
        "definition_en": (
            "Losses in first years of business.\n"
            "Can be offset against profits in later years (loss carryforward)."
        ),
        "keywords": ["anlaufverlust", "start-up losses", "gründungsverlust"],
        "related_sections": [14, 22],
    },
    
    "verlustvortrag": {
        "term_de": "Verlustvortrag",
        "term_en": "Loss carryforward",
        "definition_de": (
            "Verluste aus Vorjahren können mit Gewinnen verrechnet werden.\n"
            "Reduziert die Steuerlast in profitablen Jahren.\n\n"
            "Kein zeitliches Limit für Vortrag."
        ),
        "definition_en": (
            "Losses from previous years can offset profits.\n"
            "Reduces tax burden in profitable years.\n\n"
            "No time limit for carryforward."
        ),
        "keywords": ["verlustvortrag", "loss carryforward", "verlustverrechnung"],
        "related_sections": [14],
    },
    
    "einnahmen_überschuss": {
        "term_de": "Einnahmen-Überschuss-Rechnung",
        "term_en": "Cash-basis accounting",
        "definition_de": (
            "Siehe 'EÜR'. Einfachste Gewinnermittlung für kleine Unternehmen."
        ),
        "definition_en": (
            "See 'EÜR'. Simplest profit calculation for small businesses."
        ),
        "keywords": ["einnahmen überschuss rechnung"],
        "related_sections": [15],
    },
    
    "kassenbuch": {
        "term_de": "Kassenbuch",
        "term_en": "Cash book",
        "definition_de": (
            "Aufzeichnung aller Bargeschäfte.\n"
            "Pflicht bei regelmäßigen Bareinnahmen (z.B. Einzelhandel, Gastronomie).\n\n"
            "Elektronische Kassensysteme müssen TSE-zertifiziert sein."
        ),
        "definition_en": (
            "Record of all cash transactions.\n"
            "Required for regular cash income (e.g. retail, restaurants).\n\n"
            "Electronic cash systems must be TSE-certified."
        ),
        "keywords": ["kassenbuch", "cash book", "bareinnahmen"],
        "related_sections": [],
    },
    
    "aufbewahrungsfrist": {
        "term_de": "Aufbewahrungsfrist",
        "term_en": "Retention period",
        "definition_de": (
            "Belege müssen 10 Jahre aufbewahrt werden.\n"
            "Rechnungen, Kontoauszüge, Verträge.\n\n"
            "Bei digitaler Archivierung: Unveränderbarkeit sicherstellen."
        ),
        "definition_en": (
            "Documents must be kept for 10 years.\n"
            "Invoices, bank statements, contracts.\n\n"
            "For digital archiving: ensure immutability."
        ),
        "keywords": ["aufbewahrungsfrist", "retention period", "archivierung"],
        "related_sections": [],
    },
    
    "belegpflicht": {
        "term_de": "Belegpflicht",
        "term_en": "Document requirement",
        "definition_de": (
            "Jede Betriebsausgabe muss durch Beleg nachgewiesen werden.\n"
            "Rechnung, Quittung, oder Eigenbeleg bei Kleinbeträgen.\n\n"
            "Ohne Beleg: keine steuerliche Anerkennung."
        ),
        "definition_en": (
            "Every business expense must be documented.\n"
            "Invoice, receipt, or self-receipt for small amounts.\n\n"
            "Without document: no tax deduction."
        ),
        "keywords": ["belegpflicht", "document requirement", "nachweispflicht"],
        "related_sections": [],
    },
    
    "innergemeinschaftliche_lieferung": {
        "term_de": "Innergemeinschaftliche Lieferung (i.g. Lieferung)",
        "term_en": "Intra-community supply",
        "definition_de": (
            "Warenlieferung an Unternehmer in anderem EU-Land.\n"
            "In Deutschland steuerfrei (0% USt), wenn USt-IdNr. vorliegt.\n\n"
            "Meldung in Zusammenfassender Meldung erforderlich."
        ),
        "definition_en": (
            "Goods supply to business in another EU country.\n"
            "Tax-free in Germany (0% VAT) if VAT ID provided.\n\n"
            "Must be reported in EC sales list."
        ),
        "keywords": ["innergemeinschaftliche lieferung", "ig lieferung", "intra-community supply"],
        "related_sections": [19],
    },
    
    "innergemeinschaftlicher_erwerb": {
        "term_de": "Innergemeinschaftlicher Erwerb (i.g. Erwerb)",
        "term_en": "Intra-community acquisition",
        "definition_de": (
            "Wareneinkauf aus anderem EU-Land.\n"
            "Sie schulden deutsche USt (Erwerbsbesteuerung).\n\n"
            "Kann aber als Vorsteuer abgezogen werden (= neutral)."
        ),
        "definition_en": (
            "Goods purchase from another EU country.\n"
            "You owe German VAT (acquisition tax).\n\n"
            "But can be deducted as input VAT (= neutral)."
        ),
        "keywords": ["innergemeinschaftlicher erwerb", "ig erwerb", "intra-community acquisition"],
        "related_sections": [19],
    },
    
    "drittland": {
        "term_de": "Drittland",
        "term_en": "Third country (non-EU)",
        "definition_de": (
            "Land außerhalb der EU.\n"
            "Export: steuerfrei (0% USt) mit Ausfuhrnachweis.\n"
            "Import: Einfuhrumsatzsteuer + Zoll beim Zoll."
        ),
        "definition_en": (
            "Country outside EU.\n"
            "Export: tax-free (0% VAT) with export proof.\n"
            "Import: import VAT + customs at customs."
        ),
        "keywords": ["drittland", "third country", "non-eu", "export", "import"],
        "related_sections": [19],
    },
    
    "umsatzsteuer_regelsteuersatz": {
        "term_de": "Regelsteuersatz",
        "term_en": "Standard VAT rate",
        "definition_de": (
            "19% Umsatzsteuer auf die meisten Waren und Dienstleistungen.\n"
            "Standard-Satz in Deutschland."
        ),
        "definition_en": (
            "19% VAT on most goods and services.\n"
            "Standard rate in Germany."
        ),
        "keywords": ["regelsteuersatz", "standard rate", "19%", "19 prozent"],
        "related_sections": [18],
    },
    
    "umsatzsteuer_ermäßigt": {
        "term_de": "Ermäßigter Steuersatz",
        "term_en": "Reduced VAT rate",
        "definition_de": (
            "7% Umsatzsteuer für Lebensmittel, Bücher, Zeitungen, ÖPNV.\n"
            "Auch: kulturelle Leistungen, Pflanzenzucht."
        ),
        "definition_en": (
            "7% VAT for food, books, newspapers, public transport.\n"
            "Also: cultural services, plant cultivation."
        ),
        "keywords": ["ermäßigter steuersatz", "reduced rate", "7%", "7 prozent"],
        "related_sections": [18],
    },
    
    "steuerfreie_umsätze": {
        "term_de": "Steuerfreie Umsätze",
        "term_en": "Tax-exempt sales",
        "definition_de": (
            "Umsätze ohne USt: Versicherungen, Finanzdienstleistungen, Heilbehandlungen.\n"
            "Kein Vorsteuerabzug möglich!"
        ),
        "definition_en": (
            "Sales without VAT: insurance, financial services, medical treatment.\n"
            "No input VAT deduction possible!"
        ),
        "keywords": ["steuerfrei", "tax-exempt", "umsatzsteuerfrei"],
        "related_sections": [18],
    },
    
    "zusammenfassende_meldung": {
        "term_de": "Zusammenfassende Meldung (ZM)",
        "term_en": "EC sales list",
        "definition_de": (
            "Monatliche oder vierteljährliche Meldung aller i.g. Lieferungen.\n"
            "An Bundeszentralamt für Steuern.\n\n"
            "Pflicht bei innergemeinschaftlichen Lieferungen."
        ),
        "definition_en": (
            "Monthly or quarterly report of all intra-community supplies.\n"
            "To Federal Central Tax Office.\n\n"
            "Required for intra-community supplies."
        ),
        "keywords": ["zusammenfassende meldung", "zm", "ec sales list"],
        "related_sections": [19],
    },
    
    "gutschrift": {
        "term_de": "Gutschrift",
        "term_en": "Credit note / Self-billing",
        "definition_de": (
            "Rechnung die der EMPFÄNGER ausstellt (statt Lieferant).\n"
            "Erfordert Zustimmung des Lieferanten.\n\n"
            "Häufig bei Provisionen, Handelsvertretern."
        ),
        "definition_en": (
            "Invoice issued by RECIPIENT (instead of supplier).\n"
            "Requires supplier's consent.\n\n"
            "Common for commissions, sales representatives."
        ),
        "keywords": ["gutschrift", "credit note", "self-billing"],
        "related_sections": [],
    },
    
    "kleinbetragsrechnung": {
        "term_de": "Kleinbetragsrechnung",
        "term_en": "Small-amount invoice",
        "definition_de": (
            "Vereinfachte Rechnung bis 250 EUR (brutto).\n"
            "Weniger Pflichtangaben erforderlich.\n\n"
            "Keine Empfängeradresse nötig."
        ),
        "definition_en": (
            "Simplified invoice up to EUR 250 (gross).\n"
            "Fewer mandatory details required.\n\n"
            "No recipient address needed."
        ),
        "keywords": ["kleinbetragsrechnung", "small invoice", "vereinfachte rechnung"],
        "related_sections": [],
    },
    
    "rechnungspflichtangaben": {
        "term_de": "Rechnungspflichtangaben",
        "term_en": "Mandatory invoice details",
        "definition_de": (
            "Jede Rechnung muss enthalten:\n"
            "- Vollständige Adresse (Leistender + Empfänger)\n"
            "- Steuernummer oder USt-IdNr.\n"
            "- Rechnungsnummer (fortlaufend)\n"
            "- Leistungsdatum\n"
            "- Netto, USt-Satz, Brutto\n"
            "- Bei Kleinunternehmer: Hinweis auf §19 UStG"
        ),
        "definition_en": (
            "Every invoice must contain:\n"
            "- Full address (supplier + recipient)\n"
            "- Tax number or VAT ID\n"
            "- Invoice number (sequential)\n"
            "- Service date\n"
            "- Net, VAT rate, gross\n"
            "- For small business: reference to §19 UStG"
        ),
        "keywords": ["rechnungspflichtangaben", "invoice requirements", "pflichtangaben"],
        "related_sections": [],
    },
    
    "umsatzsteuer_voranmeldungszeitraum": {
        "term_de": "Voranmeldungszeitraum",
        "term_en": "VAT return period",
        "definition_de": (
            "Monatlich: wenn Vorjahres-USt > 7.500 EUR.\n"
            "Vierteljährlich: wenn Vorjahres-USt < 7.500 EUR.\n\n"
            "In ersten 2 Jahren immer monatlich."
        ),
        "definition_en": (
            "Monthly: if previous year VAT > EUR 7,500.\n"
            "Quarterly: if previous year VAT < EUR 7,500.\n\n"
            "First 2 years always monthly."
        ),
        "keywords": ["voranmeldungszeitraum", "return period", "meldezeitraum"],
        "related_sections": [18],
    },
    
    "skonto": {
        "term_de": "Skonto",
        "term_en": "Cash discount",
        "definition_de": (
            "Preisnachlass bei schneller Zahlung (z.B. 2% bei Zahlung innerhalb 10 Tage).\n"
            "Reduziert Bemessungsgrundlage für USt.\n\n"
            "Bei Gewährung: USt-Korrektur erforderlich."
        ),
        "definition_en": (
            "Price discount for quick payment (e.g. 2% if paid within 10 days).\n"
            "Reduces VAT base.\n\n"
            "If granted: VAT correction required."
        ),
        "keywords": ["skonto", "cash discount", "zahlungsabzug"],
        "related_sections": [],
    },
    
    "anzahlung": {
        "term_de": "Anzahlung",
        "term_en": "Advance payment / Deposit",
        "definition_de": (
            "Teilzahlung vor Leistungserbringung.\n"
            "USt entsteht bereits bei Anzahlung (wenn Ist-Versteuerung: optional).\n\n"
            "Anzahlungsrechnung erforderlich."
        ),
        "definition_en": (
            "Partial payment before service delivery.\n"
            "VAT due already at advance payment (cash-basis: optional).\n\n"
            "Advance payment invoice required."
        ),
        "keywords": ["anzahlung", "advance payment", "deposit", "vorauszahlung"],
        "related_sections": [18],
    },
    
    "differenzbesteuerung": {
        "term_de": "Differenzbesteuerung",
        "term_en": "Margin scheme",
        "definition_de": (
            "Besteuerung nur der Gewinnspanne (statt Gesamtpreis).\n"
            "Für Gebrauchtwaren, Kunst, Antiquitäten.\n\n"
            "Kein Vorsteuerabzug beim Einkauf möglich."
        ),
        "definition_en": (
            "Taxation only on profit margin (instead of total price).\n"
            "For used goods, art, antiques.\n\n"
            "No input VAT deduction on purchases possible."
        ),
        "keywords": ["differenzbesteuerung", "margin scheme", "gebrauchtwarenregelung"],
        "related_sections": [],
    },
    
    "geschäftsveräußerung_im_ganzen": {
        "term_de": "Geschäftsveräußerung im Ganzen",
        "term_en": "Transfer of business as a going concern",
        "definition_de": (
            "Verkauf eines gesamten Unternehmens (oder Teilbetriebs).\n"
            "Nicht umsatzsteuerpflichtig.\n\n"
            "Wichtig: muss alle wesentlichen Betriebsgrundlagen umfassen."
        ),
        "definition_en": (
            "Sale of entire business (or part of business).\n"
            "Not subject to VAT.\n\n"
            "Important: must include all essential business assets."
        ),
        "keywords": ["geschäftsveräußerung im ganzen", "transfer of business", "unternehmensverkauf"],
        "related_sections": [18],
    },
    
    "fragebogen_steuerliche_erfassung": {
        "term_de": "Fragebogen zur steuerlichen Erfassung",
        "term_en": "Tax registration questionnaire",
        "definition_de": (
            "Dieses Formular! Zur Anmeldung Ihrer selbständigen Tätigkeit beim Finanzamt.\n"
            "23 Abschnitte mit Fragen zu Person, Tätigkeit, Umsätzen."
        ),
        "definition_en": (
            "This form! For registering your self-employment with tax office.\n"
            "23 sections with questions about person, activity, revenue."
        ),
        "keywords": ["fragebogen", "steuerliche erfassung", "tax registration", "erfassungsbogen"],
        "related_sections": [1],
    },
    
    "elster": {
        "term_de": "ELSTER",
        "term_en": "ELSTER (electronic tax system)",
        "definition_de": (
            "Elektronisches System für Steuererklärungen.\n"
            "Pflicht für USt-Voranmeldungen und Steuererklärungen.\n\n"
            "Kostenlose Registrierung unter www.elster.de"
        ),
        "definition_en": (
            "Electronic tax declaration system.\n"
            "Required for VAT returns and tax declarations.\n\n"
            "Free registration at www.elster.de"
        ),
        "keywords": ["elster", "electronic tax", "online tax"],
        "related_sections": [],
    },
    
    "finanzamt": {
        "term_de": "Finanzamt",
        "term_en": "Tax office",
        "definition_de": (
            "Lokale Steuerbehörde zuständig für Ihr Unternehmen.\n"
            "Zuständigkeit nach Wohnsitz oder Betriebsstätte.\n\n"
            "Ihr Ansprechpartner für alle Steuerfragen."
        ),
        "definition_en": (
            "Local tax authority responsible for your business.\n"
            "Jurisdiction by residence or place of business.\n\n"
            "Your contact for all tax questions."
        ),
        "keywords": ["finanzamt", "tax office", "steuerbehörde"],
        "related_sections": [1],
    },
    
    "steuerberater": {
        "term_de": "Steuerberater",
        "term_en": "Tax advisor",
        "definition_de": (
            "Zugelassener Experte für Steuerfragen.\n"
            "Kann Sie bei Steuererklärungen, Optimierung, Betriebsprüfungen unterstützen.\n\n"
            "Kosten: je nach Umsatz und Aufwand (Steuerberatervergütungsverordnung)."
        ),
        "definition_en": (
            "Licensed expert for tax matters.\n"
            "Can help with tax returns, optimization, audits.\n\n"
            "Cost: depends on revenue and effort (fee regulation)."
        ),
        "keywords": ["steuerberater", "tax advisor", "tax consultant"],
        "related_sections": [4],
    },
    
    "identifikationsnummer": {
        "term_de": "Steuerliche Identifikationsnummer (Steuer-ID)",
        "term_en": "Tax identification number",
        "definition_de": (
            "Lebenslange 11-stellige Nummer für alle in Deutschland gemeldeten Personen.\n"
            "Erhalten Sie automatisch bei Geburt oder Anmeldung.\n\n"
            "Nicht zu verwechseln mit Steuernummer (ändert sich bei Umzug)."
        ),
        "definition_en": (
            "Lifelong 11-digit number for all persons registered in Germany.\n"
            "Received automatically at birth or registration.\n\n"
            "Not to be confused with tax number (changes when moving)."
        ),
        "keywords": ["identifikationsnummer", "steuer-id", "tax id"],
        "related_sections": [1],
    },
    
    "religion_kirchenzugehörigkeit": {
        "term_de": "Religion / Kirchenzugehörigkeit",
        "term_en": "Religion / Church membership",
        "definition_de": (
            "Bestimmt ob Sie Kirchensteuer zahlen (8-9% der Einkommensteuer).\n"
            "Gilt für Mitglieder katholischer und evangelischer Kirche.\n\n"
            "Austritt beim Standesamt möglich."
        ),
        "definition_en": (
            "Determines if you pay church tax (8-9% of income tax).\n"
            "Applies to Catholic and Protestant church members.\n\n"
            "Exit possible at registry office."
        ),
        "keywords": ["religion", "kirchenzugehörigkeit", "church membership"],
        "related_sections": [1],
    },
    
    "gewerbeanmeldung": {
        "term_de": "Gewerbeanmeldung",
        "term_en": "Trade registration",
        "definition_de": (
            "Pflicht für Gewerbetreibende (nicht Freiberufler).\n"
            "Beim Gewerbeamt/Ordnungsamt der Gemeinde.\n\n"
            "Nach Anmeldung informiert Gewerbeamt automatisch Finanzamt und IHK."
        ),
        "definition_en": (
            "Required for traders (not freelancers).\n"
            "At trade office of municipality.\n\n"
            "After registration, trade office automatically informs tax office and chamber of commerce."
        ),
        "keywords": ["gewerbeanmeldung", "trade registration", "gewerbeschein"],
        "related_sections": [7],
    },
    
    "handelsregister": {
        "term_de": "Handelsregister",
        "term_en": "Commercial register",
        "definition_de": (
            "Öffentliches Verzeichnis von Kaufleuten und Gesellschaften.\n"
            "Eintragungspflicht für Kaufleute, GmbH, AG.\n\n"
            "Einzelunternehmer: freiwillig (wird dann zum e.K.)."
        ),
        "definition_en": (
            "Public register of merchants and companies.\n"
            "Registration required for merchants, GmbH, AG.\n\n"
            "Sole proprietors: voluntary (then becomes e.K.)."
        ),
        "keywords": ["handelsregister", "commercial register", "hr"],
        "related_sections": [],
    },
    
    "ihk_handwerkskammer": {
        "term_de": "IHK / Handwerkskammer",
        "term_en": "Chamber of Commerce / Chamber of Crafts",
        "definition_de": (
            "IHK: für Gewerbetreibende (Pflichtmitgliedschaft + Beitrag).\n"
            "Handwerkskammer: für Handwerker (Pflichtmitgliedschaft + Beitrag).\n\n"
            "Freiberufler: keine Mitgliedschaft erforderlich."
        ),
        "definition_en": (
            "IHK: for traders (mandatory membership + fee).\n"
            "Chamber of Crafts: for craftsmen (mandatory membership + fee).\n\n"
            "Freelancers: no membership required."
        ),
        "keywords": ["ihk", "handwerkskammer", "chamber of commerce", "chamber of crafts"],
        "related_sections": [],
    },
    
    "betriebsnummer": {
        "term_de": "Betriebsnummer",
        "term_en": "Business number",
        "definition_de": (
            "8-stellige Nummer der Bundesagentur für Arbeit.\n"
            "Erforderlich bei Beschäftigung von Mitarbeitern.\n\n"
            "Beantragung bei Agentur für Arbeit."
        ),
        "definition_en": (
            "8-digit number from Federal Employment Agency.\n"
            "Required when employing staff.\n\n"
            "Application at employment agency."
        ),
        "keywords": ["betriebsnummer", "business number", "arbeitgebernummer"],
        "related_sections": [],
    },
    
    "geschäftsführung_vertretung": {
        "term_de": "Geschäftsführung und Vertretung",
        "term_en": "Management and representation",
        "definition_de": (
            "Bei Einzelunternehmen: Sie allein.\n"
            "Bei Gesellschaften: alle Gesellschafter oder bestellte Geschäftsführer.\n\n"
            "Wichtig für rechtliche Verpflichtungen und Haftung."
        ),
        "definition_en": (
            "For sole proprietors: you alone.\n"
            "For partnerships: all partners or appointed managers.\n\n"
            "Important for legal obligations and liability."
        ),
        "keywords": ["geschäftsführung", "vertretung", "management", "representation"],
        "related_sections": [],
    },
    
    "organschaft": {
        "term_de": "Organschaft",
        "term_en": "Tax group / Fiscal unity",
        "definition_de": (
            "Steuerliche Zusammenfassung mehrerer Unternehmen.\n"
            "Für Umsatzsteuer: keine USt zwischen den Gesellschaften.\n\n"
            "Komplex, meist nur für größere Unternehmensgruppen relevant."
        ),
        "definition_en": (
            "Tax consolidation of multiple companies.\n"
            "For VAT: no VAT between the companies.\n\n"
            "Complex, usually only relevant for larger corporate groups."
        ),
        "keywords": ["organschaft", "tax group", "fiscal unity"],
        "related_sections": [],
    },
    
    "einkünfte_aus_selbständiger_arbeit": {
        "term_de": "Einkünfte aus selbständiger Arbeit",
        "term_en": "Income from self-employment",
        "definition_de": (
            "Gewinne aus freiberuflicher Tätigkeit.\n"
            "Einkunftsart für Freiberufler.\n\n"
            "Keine Gewerbesteuer."
        ),
        "definition_en": (
            "Profits from freelance activity.\n"
            "Income type for freelancers.\n\n"
            "No trade tax."
        ),
        "keywords": ["einkünfte aus selbständiger arbeit", "self-employment income", "freiberufliche einkünfte"],
        "related_sections": [14],
    },
    
    "einkünfte_aus_gewerbebetrieb": {
        "term_de": "Einkünfte aus Gewerbebetrieb",
        "term_en": "Income from trade",
        "definition_de": (
            "Gewinne aus gewerblicher Tätigkeit.\n"
            "Einkunftsart für Gewerbetreibende.\n\n"
            "Unterliegt Gewerbesteuer."
        ),
        "definition_en": (
            "Profits from commercial activity.\n"
            "Income type for traders.\n\n"
            "Subject to trade tax."
        ),
        "keywords": ["einkünfte aus gewerbebetrieb", "trade income", "gewerbliche einkünfte"],
        "related_sections": [14],
    },
    
    "einkünfte_aus_nichtselbständiger_arbeit": {
        "term_de": "Einkünfte aus nichtselbständiger Arbeit",
        "term_en": "Income from employment",
        "definition_de": (
            "Lohn/Gehalt als Angestellter.\n"
            "Nicht relevant für dieses Formular (außer bei Nebentätigkeit)."
        ),
        "definition_en": (
            "Salary as employee.\n"
            "Not relevant for this form (except for side activity)."
        ),
        "keywords": ["einkünfte aus nichtselbständiger arbeit", "employment income", "gehalt"],
        "related_sections": [14],
    },
    
    "einkünfte_aus_kapitalvermögen": {
        "term_de": "Einkünfte aus Kapitalvermögen",
        "term_en": "Capital gains / Investment income",
        "definition_de": (
            "Zinsen, Dividenden, Aktiengewinne.\n"
            "Abgeltungssteuer: 25% (automatisch von Bank einbehalten)."
        ),
        "definition_en": (
            "Interest, dividends, stock gains.\n"
            "Flat tax: 25% (automatically withheld by bank)."
        ),
        "keywords": ["kapitalvermögen", "capital gains", "investment income", "dividenden"],
        "related_sections": [14],
    },
    
    "einkünfte_aus_vermietung": {
        "term_de": "Einkünfte aus Vermietung und Verpachtung",
        "term_en": "Rental income",
        "definition_de": (
            "Einnahmen aus Vermietung von Immobilien oder beweglichen Gütern.\n"
            "Absetzbar: AfA, Reparaturen, Verwaltungskosten."
        ),
        "definition_en": (
            "Income from renting real estate or movable assets.\n"
            "Deductible: depreciation, repairs, management costs."
        ),
        "keywords": ["vermietung", "rental income", "mieteinnahmen"],
        "related_sections": [14],
    },
    
    "sonstige_einkünfte": {
        "term_de": "Sonstige Einkünfte",
        "term_en": "Other income",
        "definition_de": (
            "Alle anderen Einkunftsarten: Renten, Unterhalt, private Veräußerungsgeschäfte.\n"
            "Freigrenze: 256 EUR/Jahr für Veräußerungsgeschäfte."
        ),
        "definition_en": (
            "All other income types: pensions, alimony, private sales.\n"
            "Exemption limit: EUR 256/year for private sales."
        ),
        "keywords": ["sonstige einkünfte", "other income", "weitere einkünfte"],
        "related_sections": [14],
    },
    
    "progressionsvorbehalt": {
        "term_de": "Progressionsvorbehalt",
        "term_en": "Progression clause",
        "definition_de": (
            "Steuerfreie Einkünfte erhöhen den Steuersatz für andere Einkünfte.\n"
            "Beispiel: Arbeitslosengeld, Elterngeld, Kurzarbeitergeld.\n\n"
            "Müssen in Steuererklärung angegeben werden."
        ),
        "definition_en": (
            "Tax-free income increases tax rate for other income.\n"
            "Example: unemployment benefit, parental benefit, short-time work.\n\n"
            "Must be declared in tax return."
        ),
        "keywords": ["progressionsvorbehalt", "progression clause"],
        "related_sections": [],
    },
    
    "freibetrag": {
        "term_de": "Freibetrag",
        "term_en": "Tax-free allowance",
        "definition_de": (
            "Betrag der steuerfrei bleibt.\n"
            "Grundfreibetrag: ~11.000 EUR (Einkommensteuer).\n"
            "Gewerbesteuerfreibetrag: 24.500 EUR."
        ),
        "definition_en": (
            "Amount that remains tax-free.\n"
            "Basic allowance: ~EUR 11,000 (income tax).\n"
            "Trade tax allowance: EUR 24,500."
        ),
        "keywords": ["freibetrag", "allowance", "tax-free amount", "grundfreibetrag"],
        "related_sections": [22],
    },
    
    "bauabzugsteuer": {
        "term_de": "Bauabzugsteuer",
        "term_en": "Construction withholding tax",
        "definition_de": (
            "15% Steuer auf Bauleistungen, vom Auftraggeber einbehalten.\n"
            "Nur bei Bauleistungen > 5.000 EUR.\n\n"
            "Kann durch Freistellungsbescheinigung vermieden werden."
        ),
        "definition_en": (
            "15% tax on construction services, withheld by client.\n"
            "Only for construction services > EUR 5,000.\n\n"
            "Can be avoided with exemption certificate."
        ),
        "keywords": ["bauabzugsteuer", "construction tax", "§48 estg"],
        "related_sections": [16],
    },
    
    "freistellungsbescheinigung": {
        "term_de": "Freistellungsbescheinigung",
        "term_en": "Exemption certificate",
        "definition_de": (
            "Befreit von Bauabzugsteuer-Einbehalt.\n"
            "Beantragung beim Finanzamt.\n\n"
            "Gültig für 3 Jahre, Verlängerung möglich."
        ),
        "definition_en": (
            "Exempts from construction tax withholding.\n"
            "Application at tax office.\n\n"
            "Valid for 3 years, extension possible."
        ),
        "keywords": ["freistellungsbescheinigung", "exemption certificate"],
        "related_sections": [16],
    },
    
    "zusammenveranlagung": {
        "term_de": "Zusammenveranlagung",
        "term_en": "Joint tax assessment (married)",
        "definition_de": (
            "Gemeinsame Steuererklärung für Ehepartner.\n"
            "Splitting-Vorteil: niedrigerer Steuersatz.\n\n"
            "Alternative: Einzelveranlagung (meist ungünstiger)."
        ),
        "definition_en": (
            "Joint tax return for spouses.\n"
            "Splitting advantage: lower tax rate.\n\n"
            "Alternative: separate assessment (usually less favorable)."
        ),
        "keywords": ["zusammenveranlagung", "joint assessment", "ehegattensplitting"],
        "related_sections": [2],
    },
    
    "splittingtarif": {
        "term_de": "Splittingtarif",
        "term_en": "Splitting rate (married)",
        "definition_de": (
            "Steuervorteil für Verheiratete bei Zusammenveranlagung.\n"
            "Gemeinsames Einkommen wird halbiert, Steuer verdoppelt.\n\n"
            "Größter Vorteil bei stark unterschiedlichen Einkommen."
        ),
        "definition_en": (
            "Tax advantage for married couples with joint assessment.\n"
            "Combined income halved, tax doubled.\n\n"
            "Greatest advantage with very different incomes."
        ),
        "keywords": ["splittingtarif", "splitting rate", "ehegattensplitting"],
        "related_sections": [2],
    },
    
    "arbeitszimmer": {
        "term_de": "Häusliches Arbeitszimmer",
        "term_en": "Home office",
        "definition_de": (
            "Absetzbar bis 1.260 EUR/Jahr (Pauschale: 1.260 EUR).\n"
            "Unbegrenzt absetzbar wenn Mittelpunkt der Tätigkeit.\n\n"
            "Voraussetzung: separater Raum, fast ausschließlich beruflich genutzt."
        ),
        "definition_en": (
            "Deductible up to EUR 1,260/year (flat rate: EUR 1,260).\n"
            "Unlimited deductible if center of activity.\n\n"
            "Requirement: separate room, almost exclusively business use."
        ),
        "keywords": ["arbeitszimmer", "home office", "häusliches arbeitszimmer"],
        "related_sections": [],
    },
    
    "homeoffice_pauschale": {
        "term_de": "Homeoffice-Pauschale",
        "term_en": "Home office flat rate",
        "definition_de": (
            "6 EUR pro Tag für bis zu 120 Tage = max. 720 EUR/Jahr.\n"
            "Seit 2023 dauerhaft.\n\n"
            "Alternative zu Arbeitszimmer wenn kein separater Raum."
        ),
        "definition_en": (
            "EUR 6 per day for up to 120 days = max. EUR 720/year.\n"
            "Permanent since 2023.\n\n"
            "Alternative to home office if no separate room."
        ),
        "keywords": ["homeoffice-pauschale", "home office flat rate"],
        "related_sections": [],
    },
    
    "fahrtkostenpauschale": {
        "term_de": "Entfernungspauschale / Fahrtkostenpauschale",
        "term_en": "Commuting allowance",
        "definition_de": (
            "0,30 EUR pro km (einfache Strecke) für Fahrten zur Arbeit.\n"
            "Ab 21. km: 0,38 EUR.\n\n"
            "Unabhängig vom Verkehrsmittel."
        ),
        "definition_en": (
            "EUR 0.30 per km (one-way) for commuting.\n"
            "From 21st km: EUR 0.38.\n\n"
            "Independent of mode of transport."
        ),
        "keywords": ["entfernungspauschale", "fahrtkostenpauschale", "commuting allowance", "pendlerpauschale"],
        "related_sections": [],
    },
    
    "reisekosten": {
        "term_de": "Reisekosten",
        "term_en": "Travel expenses",
        "definition_de": (
            "Absetzbar: Fahrt, Unterkunft, Verpflegung.\n"
            "Verpflegungspauschale: 14 EUR (8-24h), 28 EUR (>24h).\n\n"
            "Bei eigener Fahrt: 0,30 EUR/km (PKW)."
        ),
        "definition_en": (
            "Deductible: travel, accommodation, meals.\n"
            "Meal allowance: EUR 14 (8-24h), EUR 28 (>24h).\n\n"
            "Own car: EUR 0.30/km."
        ),
        "keywords": ["reisekosten", "travel expenses", "dienstreise"],
        "related_sections": [],
    },
    
    "verpflegungsmehraufwand": {
        "term_de": "Verpflegungsmehraufwand",
        "term_en": "Meal allowance (business travel)",
        "definition_de": (
            "Pauschale für Mehrkosten bei Geschäftsreisen:\n"
            "8-24 Stunden: 14 EUR\n"
            ">24 Stunden: 28 EUR pro Tag\n\n"
            "Ohne Nachweis absetzbar."
        ),
        "definition_en": (
            "Flat rate for additional meal costs on business trips:\n"
            "8-24 hours: EUR 14\n"
            ">24 hours: EUR 28 per day\n\n"
            "Deductible without receipts."
        ),
        "keywords": ["verpflegungsmehraufwand", "meal allowance", "verpflegungspauschale"],
        "related_sections": [],
    },
    
    "geschäftsausstattung": {
        "term_de": "Geschäftsausstattung",
        "term_en": "Business equipment",
        "definition_de": (
            "Büromöbel, Computer, Software, etc.\n"
            "Sofort absetzbar wenn < 800 EUR (netto).\n"
            "Sonst: AfA über Nutzungsdauer."
        ),
        "definition_en": (
            "Office furniture, computers, software, etc.\n"
            "Immediately deductible if < EUR 800 (net).\n"
            "Otherwise: depreciation over useful life."
        ),
        "keywords": ["geschäftsausstattung", "business equipment", "büroausstattung"],
        "related_sections": [],
    },
    
    "pkw_nutzung": {
        "term_de": "PKW-Nutzung (privat und geschäftlich)",
        "term_en": "Car usage (private and business)",
        "definition_de": (
            "1%-Regelung: 1% des Bruttolistenpreises pro Monat als Privatanteil.\n"
            "Fahrtenbuch: exakte Kostenaufteilung (aufwändig).\n\n"
            "Bei >50% betrieblicher Nutzung: PKW im Betriebsvermögen."
        ),
        "definition_en": (
            "1% rule: 1% of gross list price per month as private share.\n"
            "Logbook: exact cost allocation (labor-intensive).\n\n"
            "If >50% business use: car in business assets."
        ),
        "keywords": ["pkw", "1-prozent-regelung", "fahrtenbuch", "car usage"],
        "related_sections": [],
    },
    
    "bewirtungskosten": {
        "term_de": "Bewirtungskosten",
        "term_en": "Entertainment expenses",
        "definition_de": (
            "Geschäftliche Bewirtung: 70% absetzbar.\n"
            "Bewirtung von Mitarbeitern: 100% absetzbar.\n\n"
            "Nachweis erforderlich: Rechnung + Bewirtungsbeleg (wer, warum, wo)."
        ),
        "definition_en": (
            "Business entertainment: 70% deductible.\n"
            "Staff entertainment: 100% deductible.\n\n"
            "Proof required: receipt + entertainment record (who, why, where)."
        ),
        "keywords": ["bewirtungskosten", "entertainment expenses", "geschäftsessen"],
        "related_sections": [],
    },
    
    "mitarbeiter_sozialversicherung": {
        "term_de": "Mitarbeiter und Sozialversicherung",
        "term_en": "Employees and social security",
        "definition_de": (
            "Bei Anstellung von Mitarbeitern:\n"
            "- Betriebsnummer beantragen\n"
            "- Sozialversicherungsbeiträge abführen (ca. 20% des Bruttolohns)\n"
            "- Lohnsteuer anmelden und abführen\n\n"
            "Minijobs (520 EUR): pauschale Abgaben 30%."
        ),
        "definition_en": (
            "When employing staff:\n"
            "- Apply for business number\n"
            "- Pay social security contributions (~20% of gross wage)\n"
            "- Register and pay payroll tax\n\n"
            "Mini-jobs (EUR 520): flat contributions 30%."
        ),
        "keywords": ["mitarbeiter", "sozialversicherung", "employees", "social security", "lohnabrechnung"],
        "related_sections": [],
    },
    
    "kurzfristige_beschäftigung": {
        "term_de": "Kurzfristige Beschäftigung",
        "term_en": "Short-term employment",
        "definition_de": (
            "Aushilfsjobs bis 70 Tage/Jahr oder 3 Monate.\n"
            "Sozialversicherungsfrei.\n"
            "Lohnsteuer: pauschal 25% oder individuell."
        ),
        "definition_en": (
            "Temporary jobs up to 70 days/year or 3 months.\n"
            "Social security exempt.\n"
            "Payroll tax: flat 25% or individual."
        ),
        "keywords": ["kurzfristige beschäftigung", "short-term employment", "aushilfe"],
        "related_sections": [],
    },
    
    "betriebsprüfung": {
        "term_de": "Betriebsprüfung",
        "term_en": "Tax audit",
        "definition_de": (
            "Prüfung durch Finanzamt (meist nach mehreren Jahren).\n"
            "Prüfung von Buchführung, Belegen, Steuererklärungen.\n\n"
            "Bei kleinen Unternehmen selten, meist Zufallsauswahl oder Auffälligkeiten."
        ),
        "definition_en": (
            "Audit by tax office (usually after several years).\n"
            "Review of bookkeeping, receipts, tax returns.\n\n"
            "Rare for small businesses, mostly random or anomalies."
        ),
        "keywords": ["betriebsprüfung", "tax audit", "steuerprüfung"],
        "related_sections": [],
    },
}

# ─────────────────────────────────────────────────────────────────────────────
# LANGUAGE DETECTOR
# ─────────────────────────────────────────────────────────────────────────────

class LanguageDetector:
    DE_WORDS = ['der', 'die', 'das', 'ist', 'und', 'fuer', 'für', 'von', 'mit', 'zu',
                'ich', 'sie', 'abschnitt', 'feld', 'was', 'wie', 'wo', 'welche',
                'bitte', 'koennen', 'können', 'muessen', 'müssen', 'haben', 'bedeutet']
    EN_WORDS = ['the', 'is', 'and', 'for', 'of', 'with', 'to', 'in', 'i', 'you',
                'what', 'how', 'where', 'which', 'please', 'can', 'does', 'section',
                'field', 'mean', 'explain', 'show', 'tell']

    def detect(self, text: str) -> str:
        t = text.lower()
        de = sum(1 for w in self.DE_WORDS if re.search(r'\b' + re.escape(w) + r'\b', t))
        en = sum(1 for w in self.EN_WORDS if re.search(r'\b' + re.escape(w) + r'\b', t))
        return 'de' if de >= en else 'en'