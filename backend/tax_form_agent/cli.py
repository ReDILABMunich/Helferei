# ─────────────────────────────────────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────────────────────────────────────

import sys
import os
import json

# For finding data/ when installed as package
try:
    import importlib.resources as pkg_resources
except ImportError:
    import importlib_resources as pkg_resources

def get_data_path():
    """Get path to COMPLETE_FORM_STRUCTURE.json"""
    # Try package data first
    try:
        with pkg_resources.path('tax_form_agent', '../data') as p:
            data_file = p / 'COMPLETE_FORM_STRUCTURE.json'
            if data_file.exists():
                return str(data_file)
    except:
        pass
    
    # Fallback: relative to this file
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    candidates = [
        os.path.join(base, 'data', 'COMPLETE_FORM_STRUCTURE.json'),
        os.path.join(base, '..', 'data', 'COMPLETE_FORM_STRUCTURE.json'),
        'data/COMPLETE_FORM_STRUCTURE.json',
    ]
    for c in candidates:
        if os.path.exists(c):
            return c
    raise FileNotFoundError("COMPLETE_FORM_STRUCTURE.json not found")

def load_config():
    """Load config.json from current directory or package root."""
    candidates = [
        'config.json',
        os.path.join(os.path.dirname(__file__), '..', '..', 'config.json'),
    ]
    for cfg_file in candidates:
        if os.path.exists(cfg_file):
            with open(cfg_file, 'r') as f:
                cfg = json.load(f)
            key = cfg.get("openai_api_key", "").strip()
            if not key or key == "sk-...":
                print(f"ERROR: openai_api_key not set in {cfg_file}")
                print("  Edit config.json and set your OpenAI API key.")
                sys.exit(1)
            return cfg
    
    print("ERROR: config.json not found.")
    print("  Copy config.example.json to config.json and set your API key.")
    sys.exit(1)

def main():
    cfg = load_config()
    
    # Support both direct run and module import
    try:
        from .form_knowledge import FormKnowledge, FormCursor
        from .llm_client import LLMClient
        from .agent import TaxFormAgent
    except ImportError:
        # Direct run: add parent dir to path
        import sys
        import os
        sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
        from tax_form_agent.form_knowledge import FormKnowledge, FormCursor
        from tax_form_agent.llm_client import LLMClient
        from tax_form_agent.agent import TaxFormAgent

    data_file = get_data_path()
    fk    = FormKnowledge(data_file)
    llm   = LLMClient(api_key=cfg["openai_api_key"],
                      model=cfg.get("model", "gpt-4o-mini"))
    agent = TaxFormAgent(fk, llm)
    tid   = "main"
    
    if cfg.get("language") in ("de", "en"):
        agent.set_lang(cfg["language"], tid)
    
    # Welcome message
    print("\nHi! I'm your assistant for filling out the German tax registration form.\n\nI'll help you understand what each field means, what to enter, and guide you through all 23 sections step by step.\n\nIMPORTANT: This assistant is designed for the form 'Fragebogen zur steuerlichen Erfassung für Einzelunternehmen' — make sure you have selected this exact form.\n\nTIP: Start with 'section 1'. To switch to German: /lang de")

    while True:
        try:
            user_input = input("\n> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nBye!")
            break
        
        if not user_input:
            continue
        
        if user_input.startswith('/'):
            parts = user_input.split()
            cmd   = parts[0].lower()
            
            if cmd == '/quit':
                break
            elif cmd == '/reset':
                agent.reset(tid)
                print("[Session reset]")
            elif cmd == '/lang':
                if len(parts) > 1:
                    target = parts[1].lower()
                    s = agent._s(tid)
                    if target in ('de', 'en'):
                        s.lang = target
                        if target == 'de':
                            print("\nSprache auf Deutsch umgestellt. ✓\n")
                            print("Hallo! Ich bin Ihr Assistent zum Ausfüllen der deutschen Steuererklärung.\n\nIch helfe Ihnen zu verstehen, was jedes Feld bedeutet, was Sie eintragen sollen, und führe Sie durch alle 23 Abschnitte Schritt für Schritt.\n\nWICHTIG: Dieser Assistent ist für den Fragebogen zur steuerlichen Erfassung für Einzelunternehmen konzipiert — stellen Sie sicher, dass Sie genau dieses Formular ausgewählt haben.\n\nTIPP: Beginnen Sie mit 'Abschnitt 1'. Um auf Englisch zu wechseln: /lang en")
                        else:
                            print("\nLanguage switched to English. ✓\n")
                            print("Hi! I'm your assistant for filling out the German tax registration form.\n\nI'll help you understand what each field means, what to enter, and guide you through all 23 sections step by step.\n\nIMPORTANT: This assistant is designed for the form 'Fragebogen zur steuerlichen Erfassung für Einzelunternehmen' — make sure you have selected this exact form.\n\nTIP: Start with 'section 1'. To switch to German: /lang de")
                    else:
                        print("Invalid language. Use: /lang de or /lang en")
                else:
                    print("Invalid language. Use: /lang de or /lang en")         
            elif cmd == '/cursor':
                print(f"Position: {agent.get_cursor(tid)}")
                s = agent._s(tid)
                if s.last_options:
                    print(f"Options: {s.last_options[:6]}")
            elif cmd == '/back':
                s = agent._s(tid)
                if s.cursor_history:
                    old_pos = agent.get_cursor(tid)
                    prev_cursor = s.pop_cursor()
                    s.cursor = prev_cursor
                    new_pos = agent.get_cursor(tid)
                    print(f"[Went back: {old_pos} → {new_pos}]")
                    print()
                    # Render context directly without LLM
                    cursor = FormCursor.from_dict(s.cursor)
                    ctx = agent.ctx
                    fk = agent.fk
                    if cursor.field:
                        results = fk.search(cursor.field, s.lang,
                                            section_filter=cursor.section,
                                            current_section=cursor.section,
                                            current_subsection=cursor.subsection)
                        field_results = [r for r in results if r['type'] == 'field' 
                                        and r['object'].field_name == cursor.field]
                        if field_results:
                            print(ctx._field(field_results[0]['object'], s.lang))
                    elif cursor.field_group:
                        fg = fk.get_field_group(cursor.section, cursor.subsection, cursor.field_group)
                        if fg:
                            print(ctx._field_group(fg, s.lang))
                    elif cursor.subsection:
                        sub = fk.get_subsection(cursor.section, cursor.subsection)
                        if sub:
                            print(ctx._subsection(sub, s.lang))
                    elif cursor.section:
                        sec = fk.get_section(cursor.section)
                        if sec:
                            print(ctx._section(sec, s.lang))
                else:
                    print("[No history to go back to]")           
            elif cmd == '/history':
                s = agent._s(tid)
                if s.cursor_history:
                    print(f"[Cursor history ({len(s.cursor_history)} positions):]")
                    # Show most recent first (what /back would return to)
                    recent = list(reversed(s.cursor_history[-5:]))
                    for i, pos in enumerate(recent, 1):
                        bc = FormCursor.from_dict(pos).breadcrumb()
                        back_label = " ← /back goes here" if i == 1 else ""
                        print(f"  {i}. {bc}{back_label}")
                    print(f"  Current: {agent.get_cursor(tid)}")
                else:
                    print("[No navigation history yet]")
            else:
                print(f"Unknown: {cmd}")
            continue
        
        try:
            answer = agent.chat(user_input, thread_id=tid)
            print(f"\n{answer}")
        except RuntimeError as e:
            print(f"\n[API Error] {e}")
        except Exception as e:
            print(f"\n[Error] {e}")
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    main()