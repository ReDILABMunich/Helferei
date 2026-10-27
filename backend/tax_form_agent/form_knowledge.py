"""
Hierarchy:
  Section → fields / field_groups / subsections
  Subsection → fields / field_groups
  FieldGroup → fields
"""
import json
from dataclasses import dataclass, field as dc_field
from typing import Optional, List, Dict
from difflib import SequenceMatcher

# ─────────────────────────────────────────────────────────────────────────────
# DATA CLASSES
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class FormField:
    field_name: str
    field_label: str
    field_label_en: str
    field_type: str
    required: bool
    options: Optional[List[str]] = None
    options_en: Optional[List[str]] = None
    explanation: Optional[str] = None
    explanation_en: Optional[str] = None
    example: Optional[str] = None
    source: Optional[str] = None
    source_en: Optional[str] = None
    why_asked: Optional[str] = None
    why_asked_en: Optional[str] = None
    branching: Optional[dict] = None
    common_mistakes: Optional[str] = None
    common_mistakes_en: Optional[str] = None
    section_number: Optional[int] = None
    subsection_name: Optional[str] = None
    group_name: Optional[str] = None
    group_path: Optional[List[str]] = None


@dataclass
class FormFieldGroup:
    group_name: str
    group_name_en: str
    explanation: Optional[str] = None
    explanation_en: Optional[str] = None
    fields: List[FormField] = dc_field(default_factory=list)
    field_groups: List['FormFieldGroup'] = dc_field(default_factory=list)
    section_number: Optional[int] = None
    subsection_name: Optional[str] = None
    parent_group_name: Optional[str] = None


@dataclass
class FormSubsection:
    name: str
    name_en: str
    explanation: Optional[str] = None
    explanation_en: Optional[str] = None
    fields: List[FormField] = dc_field(default_factory=list)
    field_groups: List[FormFieldGroup] = dc_field(default_factory=list)
    subsections: List['FormSubsection'] = dc_field(default_factory=list)
    section_number: Optional[int] = None


@dataclass
class FormSection:
    number: int
    name: str
    name_en: str
    explanation: Optional[str] = None
    explanation_en: Optional[str] = None
    fields: List[FormField] = dc_field(default_factory=list)
    field_groups: List[FormFieldGroup] = dc_field(default_factory=list)
    subsections: List[FormSubsection] = dc_field(default_factory=list)


@dataclass
class FormCursor:
    """Current position in the form tree."""
    section: Optional[int] = None
    subsection: Optional[str] = None
    parent_subsection: Optional[str] = None
    field_group: Optional[str] = None
    field: Optional[str] = None

    def to_dict(self) -> dict:
        return {k: getattr(self, k)
                for k in ['section', 'subsection', 'parent_subsection', 'field_group', 'field']}

    @classmethod
    def from_dict(cls, d: dict) -> 'FormCursor':
        if not d:
            return cls()
        return cls(**{k: d.get(k)
                      for k in ['section', 'subsection', 'parent_subsection', 'field_group', 'field']})

    def breadcrumb(self) -> str:
        parts = []
        if self.section:            parts.append(f"Section {self.section}")
        if self.parent_subsection:  parts.append(self.parent_subsection)
        if self.subsection:         parts.append(self.subsection)
        if self.field_group:        parts.append(self.field_group)
        if self.field:              parts.append(self.field)
        return " > ".join(parts) if parts else "root"


# ─────────────────────────────────────────────────────────────────────────────
# FORM KNOWLEDGE
# ─────────────────────────────────────────────────────────────────────────────

class FormKnowledge:

    def __init__(self, structure_file: str):
        self.sections: Dict[int, FormSection] = {}
        self.all_fields: Dict[str, FormField] = {}
        self.all_subsections: Dict[str, List[FormSubsection]] = {}
        self.final_instructions: Optional[dict] = None
        self._load(structure_file)
        self._index()

    # ── Loading ───────────────────────────────────────────────────────────────

    def _load(self, path: str):
        with open(path, 'r', encoding='utf-8') as f:
            raw = json.load(f)

        for sd in raw['sections']:
            sec = FormSection(
                number=sd['number'],
                name=sd['name'],
                name_en=sd['name_en'],
                explanation=sd.get('explanation'),
                explanation_en=sd.get('explanation_en'),
            )
            for fd in sd.get('fields', []):
                sec.fields.append(self._make_field(fd, sec.number, None, None))
            for fg_d in sd.get('field_groups', []):
                sec.field_groups.append(self._load_field_group(fg_d, sec.number, None, None, []))
            for sub_d in sd.get('subsections', []):
                sec.subsections.append(self._load_subsection(sub_d, sec.number))
            self.sections[sec.number] = sec

        self.final_instructions = raw.get('final_instructions')

    def _load_subsection(self, sub_d: dict, section_num: int) -> FormSubsection:
        sub = FormSubsection(
            name=sub_d['name'],
            name_en=sub_d.get('name_en', sub_d['name']),
            explanation=sub_d.get('explanation'),
            explanation_en=sub_d.get('explanation_en'),
            section_number=section_num,
        )
        for fd in sub_d.get('fields', []):
            sub.fields.append(self._make_field(fd, section_num, sub.name, None))
        for fg_d in sub_d.get('field_groups', []):
            sub.field_groups.append(self._load_field_group(fg_d, section_num, sub.name, None, []))
        for nested_d in sub_d.get('subsections', []):
            sub.subsections.append(self._load_subsection(nested_d, section_num))
        return sub

    def _load_field_group(self, fg_d: dict, section_num: int, sub_name: Optional[str],
                           parent_group: Optional[str], parent_path: list) -> FormFieldGroup:
        fg = FormFieldGroup(
            group_name=fg_d['group_name'],
            group_name_en=fg_d.get('group_name_en', fg_d['group_name']),
            explanation=fg_d.get('explanation'),
            explanation_en=fg_d.get('explanation_en'),
            section_number=section_num,
            subsection_name=sub_name,
            parent_group_name=parent_group,
        )
        this_path = parent_path + [fg.group_name]
        for fd in fg_d.get('fields', []):
            fg.fields.append(self._make_field(fd, section_num, sub_name, fg.group_name, group_path=this_path))
        for nested_fg_d in fg_d.get('field_groups', []):
            fg.field_groups.append(self._load_field_group(nested_fg_d, section_num, sub_name, fg.group_name, this_path))
        return fg

    def _make_field(self, fd: dict, section_num: int, sub_name: Optional[str],
                    group_name: Optional[str], group_path: Optional[list] = None) -> FormField:
        return FormField(
            field_name=fd['field_name'],
            field_label=fd['field_label'],
            field_label_en=fd.get('field_label_en', fd['field_label']),
            field_type=fd.get('field_type', 'text'),
            required=fd.get('required', False),
            options=fd.get('options'),
            options_en=fd.get('options_en'),
            explanation=fd.get('explanation'),
            explanation_en=fd.get('explanation_en'),
            example=fd.get('example'),
            source=fd.get('source'),
            source_en=fd.get('source_en'),
            why_asked=fd.get('why_asked'),
            why_asked_en=fd.get('why_asked_en'),
            branching=fd.get('branching'),
            common_mistakes=fd.get('common_mistakes'),
            common_mistakes_en=fd.get('common_mistakes_en'),
            section_number=section_num,
            subsection_name=sub_name,
            group_name=group_name,
            group_path=group_path or ([group_name] if group_name else []),
        )

    # ── Indexing ──────────────────────────────────────────────────────────────

    def _index(self):
        def index_field_group(fg: FormFieldGroup):
            for f in fg.fields:
                self.all_fields[f.field_name] = f
            for nested in fg.field_groups:
                index_field_group(nested)

        def index_subsection(sub: FormSubsection):
            self.all_subsections.setdefault(sub.name, []).append(sub)
            for f in sub.fields:
                self.all_fields[f.field_name] = f
            for fg in sub.field_groups:
                index_field_group(fg)
            for nested_sub in sub.subsections:
                index_subsection(nested_sub)

        for sec in self.sections.values():
            for f in sec.fields:
                self.all_fields[f.field_name] = f
            for fg in sec.field_groups:
                index_field_group(fg)
            for sub in sec.subsections:
                index_subsection(sub)

    # ── Getters ───────────────────────────────────────────────────────────────

    def get_section(self, n: int) -> Optional[FormSection]:
        return self.sections.get(n)

    def get_subsection(self, sec_num: int, name: str) -> Optional[FormSubsection]:
        sec = self.get_section(sec_num)
        if not sec:
            return None

        def find_in(subs, name):
            for sub in subs:
                if sub.name == name:
                    return sub
                found = find_in(sub.subsections, name)
                if found:
                    return found
            return None

        return find_in(sec.subsections, name)

    def get_field_group(self, sec_num: int, sub_name: Optional[str],
                        grp_name: str) -> Optional[FormFieldGroup]:
        if sub_name:
            sub = self.get_subsection(sec_num, sub_name)
            if not sub:
                return None
            for fg in sub.field_groups:
                if fg.group_name == grp_name:
                    return fg
        else:
            sec = self.get_section(sec_num)
            if sec:
                for fg in sec.field_groups:
                    if fg.group_name == grp_name:
                        return fg
        return None

    def get_field(self, name: str) -> Optional[FormField]:
        return self.all_fields.get(name)

    def get_field_by_cursor(self, sec_num: Optional[int],
                            sub_name: Optional[str],
                            grp_name: Optional[str],
                            field_name: str) -> Optional[FormField]:
        """Resolve a field by its full path. Many fields share field_name
        across sections (e.g. 'art', 'postleitzahl', 'strasse'), so
        get_field(name) alone returns the wrong one. This walks the actual
        tree using the cursor's section/subsection/group context."""
        if not sec_num:
            return self.all_fields.get(field_name)

        def _find_in_group(fg: FormFieldGroup) -> Optional[FormField]:
            for f in fg.fields:
                if f.field_name == field_name:
                    return f
            for nested in fg.field_groups:
                hit = _find_in_group(nested)
                if hit:
                    return hit
            return None

        def _find_in_subsection(sub) -> Optional[FormField]:
            for f in sub.fields:
                if f.field_name == field_name:
                    return f
            if grp_name:
                for fg in sub.field_groups:
                    if fg.group_name == grp_name:
                        hit = _find_in_group(fg)
                        if hit:
                            return hit
            else:
                for fg in sub.field_groups:
                    hit = _find_in_group(fg)
                    if hit:
                        return hit
            if hasattr(sub, 'subsections') and sub.subsections:
                for nested_sub in sub.subsections:
                    hit = _find_in_subsection(nested_sub)
                    if hit:
                        return hit
            return None

        sec = self.get_section(sec_num)
        if not sec:
            return self.all_fields.get(field_name)

        # Direct fields at section level
        for f in sec.fields:
            if f.field_name == field_name:
                return f

        # Subsection-scoped
        if sub_name:
            for sub in sec.subsections:
                if sub.name == sub_name:
                    hit = _find_in_subsection(sub)
                    if hit:
                        return hit
                # Search nested subsections too
                if hasattr(sub, 'subsections') and sub.subsections:
                    for nested in sub.subsections:
                        if nested.name == sub_name:
                            hit = _find_in_subsection(nested)
                            if hit:
                                return hit
        else:
            # No subsection given — try direct section-level field groups
            for fg in sec.field_groups:
                if grp_name and fg.group_name == grp_name:
                    hit = _find_in_group(fg)
                    if hit:
                        return hit
                elif not grp_name:
                    hit = _find_in_group(fg)
                    if hit:
                        return hit

        # Fallback: scan whole section
        for sub in sec.subsections:
            hit = _find_in_subsection(sub)
            if hit:
                return hit
        for fg in sec.field_groups:
            hit = _find_in_group(fg)
            if hit:
                return hit

        return self.all_fields.get(field_name)

    # ── Search ────────────────────────────────────────────────────────────────

    def search(self, query: str, lang: str = 'en',
               section_filter: Optional[int] = None,
               current_section: Optional[int] = None,
               current_subsection: Optional[str] = None,
               current_field_group: Optional[str] = None) -> List[dict]:
        q = query.lower().strip()
        results = []

        for sn, section in self.sections.items():
            if section_filter and sn != section_filter:
                continue

            ctx_boost = 1.5 if (current_section and sn == current_section) else 1.0

            # Use German name only when lang='de'
            sec_names = [section.name] if lang == 'de' else [section.name, section.name_en]
            s = self._score(q, sec_names)
            if s > 0:
                sec_boost = 1.0 if (current_section and sn == current_section) else ctx_boost
                results.append({'type': 'section', 'object': section, 'score': s * sec_boost, 'section': sn})

            # Fields at section level
            for f in section.fields:
                s = self._score_field(q, f, lang)
                if s > 0:
                    results.append({'type': 'field', 'object': f, 'score': s * ctx_boost, 'section': sn})

            # Field groups at section level
            for fg in section.field_groups:
                self._search_field_group(fg, sn, None, ctx_boost, 1.0, current_field_group, q, results, lang=lang)

            # Subsections
            for sub in section.subsections:
                sub_boost = 2.0 if (current_section and sn == current_section and
                                    current_subsection and sub.name == current_subsection) else 1.0
                self._search_subsection(sub, sn, ctx_boost * sub_boost, current_field_group, q, results, lang=lang)

        results.sort(key=lambda x: x['score'], reverse=True)
        return results

    def _search_subsection(self, sub: FormSubsection, sn: int, parent_boost: float,
                            current_field_group: Optional[str], q: str, results: list,
                            lang: str = 'en'):
        # Use German name only when lang='de'
        sub_names = [sub.name] if lang == 'de' else [sub.name, sub.name_en]
        s = self._score(q, sub_names)
        if s > 0:
            results.append({'type': 'subsection', 'object': sub,
                            'score': s * parent_boost, 'section': sn, 'subsection': sub.name})

        for f in sub.fields:
            s = self._score_field(q, f, lang)
            if s > 0:
                results.append({'type': 'field', 'object': f,
                                'score': s * parent_boost, 'section': sn, 'subsection': sub.name})

        for fg in sub.field_groups:
            self._search_field_group(fg, sn, sub.name, parent_boost, 1.0, current_field_group, q, results, lang=lang)

        for nested in sub.subsections:
            self._search_subsection(nested, sn, parent_boost * 1.5, current_field_group, q, results, lang=lang)

    def _search_field_group(self, fg: FormFieldGroup, sn: int, sub_name: Optional[str],
                             parent_boost: float, fg_boost: float,
                             current_field_group: Optional[str], q: str, results: list,
                             parent_fg_path: Optional[list] = None, lang: str = 'en'):
        this_path = (parent_fg_path or []) + [fg.group_name]
        in_cursor_path = bool(current_field_group and current_field_group in this_path)
        boost = parent_boost * (3.0 if in_cursor_path else 1.0)

        # Use German name only when lang='de'
        fg_names = [fg.group_name] if lang == 'de' else [fg.group_name, fg.group_name_en]
        fg_score = self._score(q, fg_names)
        if fg_score >= 100:
            results.append({'type': 'field_group', 'object': fg,
                            'score': fg_score * boost * 1.5,
                            'section': sn, 'subsection': sub_name, 'field_group': fg.group_name})
            for nested in fg.field_groups:
                self._search_field_group(nested, sn, sub_name, boost, 1.0, current_field_group, q, results, this_path, lang=lang)
            return
        elif fg_score > 0:
            results.append({'type': 'field_group', 'object': fg,
                            'score': fg_score * boost,
                            'section': sn, 'subsection': sub_name, 'field_group': fg.group_name})

        for f in fg.fields:
            s = self._score_field(q, f, lang)
            if s > 0:
                field_boost = 3.0 if (current_field_group and current_field_group in (f.group_path or [])) else 1.0
                results.append({'type': 'field', 'object': f,
                                'score': s * boost * field_boost,
                                'section': sn, 'subsection': sub_name, 'group': fg.group_name})

        for nested in fg.field_groups:
            self._search_field_group(nested, sn, sub_name, boost, 1.0, current_field_group, q, results, this_path, lang=lang)

    # ── Scoring ───────────────────────────────────────────────────────────────

    _STOP_WORDS = frozenset(
        "ich du er sie es wir ihr mein dein sein ihr uns euch"
        " der die das den dem des ein eine einer einem einen"
        " und oder aber auch noch schon nicht kein keine"
        " in an auf zu von mit für um bei nach über aus"
        " bin ist hat habe haben wird werden war wurde"
        " ja nein ok dass wenn als ob wie was wer wo"
        " the a an is are was were has have do does"
        " i you he she it we they my your his her our"
        " and or but not no yes if when how what where who"
        " to of in on at by for with from".split()
    )

    @staticmethod
    def _normalize(text: str) -> str:
        """Normalize German characters for tolerant matching."""
        return (text.lower()
                .replace("ß", "ss").replace("ä", "ae").replace("ö", "oe")
                .replace("ü", "ue"))

    def _score(self, q: str, names: List[str]) -> float:
        best = 0.0
        q_norm = self._normalize(q)
        for n in (names or []):
            if not n:
                continue
            nl = n.lower()
            nl_norm = self._normalize(n)
            # Exact match (with and without normalization)
            if q == nl or q_norm == nl_norm:
                best = max(best, 100)
                continue
            # Query is substring of name
            if q in nl or q_norm in nl_norm:
                best = max(best, 60)
                continue
            # Name starts with query (user copied beginning of long name)
            if len(q) >= 5 and (nl.startswith(q) or nl_norm.startswith(q_norm)):
                best = max(best, 75)
                continue
            # Word-level rules (filter out stop words)
            n_words = set(nl.split()) - self._STOP_WORDS
            q_words = set(q.split()) - self._STOP_WORDS
            if not n_words or not q_words:
                continue
            if n_words.issubset(q_words):
                best = max(best, 40)
                continue
            if q_words.issubset(n_words):
                best = max(best, 40)
                continue
            # Word overlap — minimum 50% coverage
            overlap = len(n_words & q_words)
            if overlap > 0:
                coverage = overlap / max(len(n_words), len(q_words))
                if coverage >= 0.5:
                    best = max(best, int(coverage * 30))
            # Fuzzy match on full query (with normalization)
            ratio = SequenceMatcher(None, q_norm, nl_norm).ratio()
            if ratio >= 0.7:
                best = max(best, int(ratio * 70))
            # Fuzzy match — all query words must find a pair
            n_words_norm = set(nl_norm.split()) - self._STOP_WORDS
            q_words_norm = set(q_norm.split()) - self._STOP_WORDS
            if len(q_words_norm) >= 1 and len(n_words_norm) >= 1:
                word_matches = sum(
                    1 for qw in q_words_norm
                    if any(SequenceMatcher(None, qw, nw).ratio() >= 0.75
                           for nw in n_words_norm)
                )
                if word_matches == len(q_words_norm):
                    coverage = word_matches / max(len(q_words_norm),
                                                  len(n_words_norm))
                    best = max(best, int(coverage * 60))
            # Fuzzy match — at least one word pair (min 3 chars)
            if len(q_words_norm) >= 1 and len(n_words_norm) >= 1:
                best_word_match = max(
                    (SequenceMatcher(None, qw, nw).ratio()
                     for qw in q_words_norm for nw in n_words_norm
                     if len(qw) >= 3 and len(nw) >= 3),
                    default=0
                )
                if best_word_match >= 0.85:
                    best = max(best, int(best_word_match * 50))
        return best

    def _score_field(self, q: str, f: FormField, lang: str = 'de') -> float:
        if lang == 'de':
            return self._score(q, [f.field_label, f.field_name])
        else:
            return self._score(q, [f.field_label, f.field_label_en, f.field_name])