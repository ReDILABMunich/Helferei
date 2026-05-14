"""
Tax Form Assistant — PyQt6 GUI
Run:  python src/tax_form_agent/gui_qt.py
"""
import html as _html_mod
import json
import os
import re
import subprocess
import sys
import threading

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QScrollArea, QLabel, QTextEdit, QPushButton, QFrame, QSizePolicy,
    QLineEdit, QDialog, QCheckBox, QMessageBox,
)
from PyQt6.QtCore import Qt, pyqtSignal, QObject, QTimer, QEvent
from PyQt6.QtGui import QFont, QFontDatabase, QCursor

# ── Palette ──────────────────────────────────────────────────────────────
C_ACCENT     = "#4A7CF7"
C_WIN_BG     = "#FFFFFF"
C_TOPBAR     = "#FFFFFF"
C_DIVIDER    = "#E4E6EA"
C_CHAT_BG    = "#F5F5F7"
C_USER_BG    = "#2B4C8A"
C_USER_FG    = "#FFFFFF"
C_BOT_BG     = "#FFFFFF"
C_BOT_FG     = "#1C1E21"
C_BOT_BORDER = "#E5E5EA"
C_BLUE       = "#2B4C8A"
C_BLUE_HOV   = "#1E3A6E"
C_SYS_FG     = "#A0A8B4"
C_HINT_BG    = "#EDF1F9"
C_HINT_FG    = "#3D5A8A"
C_INPUT_BG   = "#EFF1F4"

FONT_FAMILY = "DM Sans"

HINT_EN = 'Navigate by section number, German field name, or ask any question  ·  e.g. “7”, “Geburtsdatum”, “what is IBAN?”'
HINT_DE = 'Navigation per Abschnittsnummer, deutschem Feldnamen oder Frage  ·  z.B. „7“, „Geburtsdatum“, „was ist IBAN?“'


# ── Paths ─────────────────────────────────────────────────────────────────

def _app_dir() -> str:
    if getattr(sys, '_MEIPASS', None):
        return sys._MEIPASS
    return os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def _config_path() -> str:
    if getattr(sys, '_MEIPASS', None):
        if sys.platform == "win32":
            app_support = os.path.join(os.environ.get("APPDATA",
                                       os.path.expanduser("~")), "Bruno")
        else:
            app_support = os.path.join(os.path.expanduser("~"),
                                       "Library", "Application Support", "Bruno")
        os.makedirs(app_support, exist_ok=True)
        return os.path.join(app_support, "config.json")
    root = _app_dir()
    for c in [os.path.join(root, "config.json"), "config.json"]:
        if os.path.exists(c):
            return os.path.abspath(c)
    return os.path.join(root, "config.json")


def _data_path() -> str:
    root = _app_dir()
    for c in [
        os.path.join(root, "data", "COMPLETE_FORM_STRUCTURE.json"),
        os.path.join(root, "..", "data", "COMPLETE_FORM_STRUCTURE.json"),
        "data/COMPLETE_FORM_STRUCTURE.json",
    ]:
        if os.path.exists(c):
            return os.path.abspath(c)
    raise FileNotFoundError("COMPLETE_FORM_STRUCTURE.json not found")


def load_config():
    path = _config_path()
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f), path
    return {"openai_api_key": "", "model": "gpt-4o-mini", "language": "en"}, path


def save_config(cfg, path):
    with open(path, "w") as f:
        json.dump(cfg, f, indent=2)


def _install_fonts():
    root = _app_dir() if getattr(sys, '_MEIPASS', None) else \
           os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    fonts_dir = os.path.join(root, "fonts")
    if not os.path.isdir(fonts_dir):
        return
    for f in os.listdir(fonts_dir):
        if f.endswith(".ttf"):
            QFontDatabase.addApplicationFont(os.path.join(fonts_dir, f))


# ── Clipboard helpers ─────────────────────────────────────────────────────

def clipboard_copy(text: str):
    try:
        if sys.platform == "darwin":
            subprocess.run(["pbcopy"], input=text.encode("utf-8"), timeout=1)
        elif sys.platform == "win32":
            subprocess.run(["clip"], input=text.encode("utf-16le"), timeout=1)
        else:
            subprocess.run(["xclip", "-selection", "clipboard"],
                           input=text.encode("utf-8"), timeout=1)
    except Exception:
        pass


def clipboard_paste() -> str:
    try:
        if sys.platform == "darwin":
            return subprocess.run(["pbpaste"], capture_output=True,
                                  text=True, timeout=1).stdout
        elif sys.platform == "win32":
            return subprocess.run(
                ["powershell", "-command", "Get-Clipboard"],
                capture_output=True, text=True, timeout=2,
            ).stdout.rstrip("\r\n")
        else:
            return subprocess.run(
                ["xclip", "-selection", "clipboard", "-o"],
                capture_output=True, text=True, timeout=1,
            ).stdout
    except Exception:
        return ""


# ── Bubble widgets ────────────────────────────────────────────────────────

class BotBubble(QTextEdit):
    """Bot chat bubble. Uses QTextEdit (read-only) instead of QLabel because
    QLabel's rich-text rendering reserves inconsistent trailing space at the
    bottom — the gap varies between bubbles depending on content structure
    (bullets vs paragraphs, presence of bold runs at wrap points, etc.).
    QTextEdit exposes the QTextDocument directly, lets us pin documentMargin
    to 0, and gives us the exact document size for height snapping."""

    PADDING_H = 14
    PADDING_V = 12

    def __init__(self, html: str, parent=None):
        super().__init__(parent)
        self.setReadOnly(True)
        # No scrollbars: we size the widget to fit content via setFixedHeight.
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        # Default cursor (no I-beam) — still allow text selection for copy.
        self.viewport().setCursor(QCursor(Qt.CursorShape.ArrowCursor))
        # Default frame conflicts with our CSS border; turn it off.
        self.setFrameShape(QFrame.Shape.NoFrame)
        # Pin internal document margin to 0 — we control vertical padding via
        # CSS. This is the key reason for using QTextEdit over QLabel.
        self.document().setDocumentMargin(0)
        # QTextEdit defaults to (Expanding, Expanding) which makes it grow to
        # fill any space the layout gives it. We size the widget explicitly
        # via setFixedWidth / setFixedHeight, so fix the policy accordingly.
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        # Intercept wheel events on the viewport — without this, scrolling
        # over the bubble scrolls the bubble's INTERNAL document instead of
        # the chat ScrollArea, and the text appears to "disappear".
        self.viewport().installEventFilter(self)
        self.setHtml(html)
        self.setStyleSheet(f"""
            BotBubble {{
                background-color: {C_BOT_BG};
                color: {C_BOT_FG};
                border: 1px solid {C_BOT_BORDER};
                border-radius: 12px;
                padding: {self.PADDING_V}px {self.PADDING_H}px;
                font-family: "{FONT_FAMILY}";
                font-size: 16px;
            }}
        """)

    def content_height(self) -> int:
        """Exact pixel height the document needs at the current width."""
        return int(self.document().size().height()) + 2 * self.PADDING_V

    def wheelEvent(self, event):
        """Let mouse-wheel scrolling propagate to the chat's ScrollArea."""
        event.ignore()

    def keyPressEvent(self, event):
        """After Ctrl+C, clear the selection so the highlight goes away.
        Qt's default keeps the selection visible indefinitely until the
        user clicks elsewhere, which feels stuck when copying repeatedly."""
        super().keyPressEvent(event)
        from PyQt6.QtGui import QKeySequence
        if event.matches(QKeySequence.StandardKey.Copy):
            cursor = self.textCursor()
            cursor.clearSelection()
            self.setTextCursor(cursor)

    def contextMenuEvent(self, event):
        """Same treatment for Copy invoked via the right-click context menu —
        clear the selection after the menu's copy action runs."""
        menu = self.createStandardContextMenu()
        menu.exec(event.globalPos())
        cursor = self.textCursor()
        cursor.clearSelection()
        self.setTextCursor(cursor)

    def focusOutEvent(self, event):
        """Clear the selection when this bubble loses focus — by default Qt
        keeps the highlight visible indefinitely until the user clicks back
        inside. That feels stuck when the user selected text just to read
        it, then clicked elsewhere without copying."""
        cursor = self.textCursor()
        cursor.clearSelection()
        self.setTextCursor(cursor)
        super().focusOutEvent(event)

    def eventFilter(self, obj, event):
        """Intercept wheel events on the viewport and forward them to the
        ancestor ScrollArea — Qt's default QAbstractScrollArea behavior is
        to scroll the viewport's content, which would scroll the bubble's
        internal document and hide our text."""
        if obj is self.viewport() and event.type() == QEvent.Type.Wheel:
            ancestor = self.parentWidget()
            while ancestor is not None:
                if isinstance(ancestor, QScrollArea):
                    QApplication.sendEvent(ancestor.viewport(), event)
                    return True
                ancestor = ancestor.parentWidget()
        return False


class UserBubble(QLabel):
    def __init__(self, text: str, parent=None):
        super().__init__(parent)
        self.setText(text)
        self.setWordWrap(True)
        self.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse
        )
        self.setStyleSheet(f"""
            UserBubble {{
                background-color: {C_USER_BG};
                color: {C_USER_FG};
                border-radius: 8px;
                padding: 8px 14px;
                font-family: "{FONT_FAMILY}";
                font-size: 16px;
            }}
        """)


class SysLabel(QLabel):
    def __init__(self, text: str, parent=None):
        super().__init__(f"— {text} —", parent)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setStyleSheet(f"""
            QLabel {{
                color: {C_SYS_FG};
                font-family: "{FONT_FAMILY}";
                font-size: 12px;
            }}
        """)


# ── HTML formatting for bot messages ─────────────────────────────────────

_STRUCT_RE = re.compile(
    r"(?:Section|Abschnitt|Subsection|Unterabschnitt"
    r"|[Ff]ield(?:\s+group)?|Feld(?:gruppe)?)"
    r"\s+(?:\d+\s+)?'([^']+)'"
)


def _esc(s: str) -> str:
    return _html_mod.escape(s, quote=False)


def _blue(s: str) -> str:
    return f'<b style="color:{C_BLUE}">{_esc(s)}</b>'


def format_bot_html(text: str, current_name: str = "") -> str:
    """Convert plain agent text to HTML with bold-blue German names."""
    def format_line(line: str) -> str:
        if line.startswith("'"):
            m = re.match(r"'([^']+)'(.*)", line, re.DOTALL)
            if m:
                return _blue(m.group(1)) + _esc(m.group(2))
        # Replace "Section 'X'" patterns with bold blue name
        result = []
        pos = 0
        for m in _STRUCT_RE.finditer(line):
            result.append(_esc(line[pos:m.start()]))
            prefix = m.group(0).split("'")[0]
            suffix = m.group(0).rsplit("'", 1)[1] if "'" in m.group(0) else ""
            result.append(_esc(prefix) + _blue(m.group(1)) + _esc(suffix))
            pos = m.end()
        result.append(_esc(line[pos:]))
        return "".join(result) if any(result) else _esc(line)

    # Highlight first line if it equals the current cursor name (long field names
    # that LLM emits unquoted). Normalize by stripping trailing period/quotes.
    def _norm(s: str) -> str:
        return s.strip().strip("'\"").rstrip(".").strip().lower()
    cur_norm = _norm(current_name) if current_name else ""

    out = []
    first_non_empty_seen = False
    for line in text.split("\n"):
        if not line.strip():
            out.append("")
            continue
        # Blue-highlight the very first line ONLY when it is the bare field
        # name on its own (no quotes, no trailing text). Quoted variants are
        # handled by the existing "line.startswith('\\'')" branch below.
        if (not first_non_empty_seen and cur_norm and len(cur_norm) >= 3
                and not line.lstrip().startswith(("'", '"'))):
            first_non_empty_seen = True
            if _norm(line) == cur_norm:
                out.append(_blue(line.strip()))
                continue
        first_non_empty_seen = True
        if line.startswith("• "):
            content = line[2:]
            if " · " in content or " | " in content:
                sep = " · " if " · " in content else " | "
                de_part, rest = content.split(sep, 1)
                s = "•  " + _blue(de_part)
                if " — " in rest:
                    en_part, desc = rest.split(" — ", 1)
                    s += f" · {_esc(en_part)} — {_esc(desc)}"
                else:
                    s += f" · {_esc(rest)}"
                out.append(s)
            elif " — " in content:
                name, desc = content.split(" — ", 1)
                out.append("•  " + _blue(name) + f" — {_esc(desc)}")
            elif "→" in content or re.match(r'^(Section|Abschnitt)\s+\d+\s*:', content):
                out.append("•  " + _esc(content))
            else:
                out.append("•  " + _blue(content))
        else:
            out.append(format_line(line))
    # Trim trailing empty entries — these would otherwise become trailing
    # <br> tags in the joined HTML, which Qt renders as extra blank space
    # at the bottom of the bubble.
    while out and not out[-1].strip():
        out.pop()
    html = "<br>".join(out)
    # Belt-and-braces: also strip any trailing <br> tags that survived.
    html = re.sub(r'(<br\s*/?>)+\s*$', '', html)
    return html


# ── Signals for thread-safe UI updates ───────────────────────────────────

class AgentSignals(QObject):
    # First arg is the request generation captured by the worker — used by
    # the main-thread handlers to drop signals that belong to a request
    # that's already been invalidated by Reset / language toggle / API change.
    reply_ready = pyqtSignal(int, str)
    chunk_arrived = pyqtSignal(int, str)
    auth_failed = pyqtSignal(int)


# ── Main window ───────────────────────────────────────────────────────────

class ChatWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Bruno")
        self.resize(920, 700)
        # Centre on screen
        screen = QApplication.primaryScreen().availableGeometry()
        self.move(
            (screen.width() - self.width()) // 2,
            (screen.height() - self.height()) // 2,
        )

        self.cfg, self.cfg_path = load_config()
        self.lang = self.cfg.get("language", "en")
        self.agent = None
        self.tid = "main"
        self.signals = AgentSignals()
        self.signals.reply_ready.connect(self._on_reply)
        self.signals.chunk_arrived.connect(self._on_chunk)
        self.signals.auth_failed.connect(self._on_auth_failed)
        # When streaming is in progress, point this at the bubble being built.
        self._stream_bubble = None
        self._stream_buffer = ""
        # Generation counter — bumped on Reset/lang toggle/API change to
        # invalidate any in-flight worker. The worker captures this at start
        # and gates its chunk/reply emissions; main-thread handlers also
        # check it and drop signals that no longer belong to the current
        # request. Prevents stale streaming chunks from being injected into
        # a chat that was just cleared, and avoids RuntimeError on access
        # to widgets the reset already deleteLater()'d.
        self._stream_gen = 0

        central = QWidget()
        central.setStyleSheet(f"background-color: {C_WIN_BG};")
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # ── Top bar ───────────────────────────────────────────────────────
        top_bar = QWidget()
        top_bar.setStyleSheet(f"background-color: {C_TOPBAR};")
        top_layout = QHBoxLayout(top_bar)
        top_layout.setContentsMargins(20, 12, 20, 8)
        top_layout.setSpacing(0)

        title_col = QVBoxLayout()
        title_col.setSpacing(4)
        self.title_lbl = QLabel(
            "Fragebogen zur steuerlichen Erfassung für Einzelunternehmen"
        )
        self.title_lbl.setStyleSheet(
            f'font-family: "{FONT_FAMILY}"; font-size: 16px; color: #333;'
        )
        self.title_lbl.setWordWrap(True)
        title_col.addWidget(self.title_lbl)

        self.breadcrumb_lbl = QLabel("")
        self.breadcrumb_lbl.setStyleSheet(
            f'font-family: "{FONT_FAMILY}"; font-size: 14px; color: #666;'
        )
        self.breadcrumb_lbl.setTextFormat(Qt.TextFormat.RichText)
        self.breadcrumb_lbl.setWordWrap(True)
        self.breadcrumb_lbl.setMouseTracking(True)
        self.breadcrumb_lbl.linkActivated.connect(self._on_breadcrumb_click)
        self.breadcrumb_lbl.linkHovered.connect(self._on_breadcrumb_hover)
        self._bc_hover = None
        title_col.addWidget(self.breadcrumb_lbl)
        top_layout.addLayout(title_col, 1)

        # Buttons
        btn_style = f"""
            QPushButton {{
                background-color: transparent;
                color: #666;
                border: 1px solid #D1D1D6;
                border-radius: 16px;
                padding: 4px 14px;
                font-family: "{FONT_FAMILY}"; font-size: 16px;
            }}
            QPushButton:hover {{ background-color: #EAEAEA; }}
        """
        self.lang_btn = QPushButton("DE")
        self.lang_btn.setFixedHeight(32)
        self.lang_btn.setStyleSheet(btn_style)
        self.lang_btn.clicked.connect(self._toggle_lang)
        top_layout.addWidget(self.lang_btn)
        top_layout.addSpacing(6)

        reset_btn = QPushButton("Reset")
        reset_btn.setFixedHeight(32)
        reset_btn.setStyleSheet(btn_style)
        reset_btn.clicked.connect(self._reset_chat)
        top_layout.addWidget(reset_btn)
        top_layout.addSpacing(6)

        api_btn = QPushButton("API")
        api_btn.setFixedHeight(32)
        api_btn.setStyleSheet(btn_style)
        api_btn.clicked.connect(self._open_settings)
        top_layout.addWidget(api_btn)

        layout.addWidget(top_bar)

        # Divider
        div = QFrame()
        div.setFrameShape(QFrame.Shape.HLine)
        div.setStyleSheet(f"color: {C_DIVIDER}; background-color: {C_DIVIDER};")
        div.setFixedHeight(1)
        layout.addWidget(div)

        # ── Chat area ─────────────────────────────────────────────────────
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.scroll.setStyleSheet(f"""
            QScrollArea {{
                background-color: {C_CHAT_BG};
                border: none;
            }}
            QScrollBar:vertical {{
                background: transparent;
                width: 10px;
                margin: 4px 2px 4px 0;
            }}
            QScrollBar::handle:vertical {{
                background: #C0C0C6;
                border-radius: 4px;
                min-height: 30px;
            }}
            QScrollBar::handle:vertical:hover {{
                background: #A0A0A6;
            }}
            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {{
                height: 0;
                background: none;
                border: none;
            }}
            QScrollBar::add-page:vertical,
            QScrollBar::sub-page:vertical {{
                background: none;
            }}
        """)
        self.scroll.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAsNeeded
        )
        self.scroll.verticalScrollBar().setSingleStep(20)

        self.chat_container = QWidget()
        self.chat_container.setStyleSheet(f"background-color: {C_CHAT_BG};")
        self.chat_layout = QVBoxLayout(self.chat_container)
        self.chat_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.chat_layout.setContentsMargins(20, 12, 20, 12)
        self.chat_layout.setSpacing(8)
        self.scroll.setWidget(self.chat_container)
        layout.addWidget(self.scroll, 1)

        # ── Hint bar ──────────────────────────────────────────────────────
        self.hint_lbl = QLabel(HINT_EN if self.lang == "en" else HINT_DE)
        self.hint_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.hint_lbl.setWordWrap(True)
        self.hint_lbl.setStyleSheet(f"""
            QLabel {{
                background-color: {C_HINT_BG};
                color: {C_HINT_FG};
                font-family: "{FONT_FAMILY}"; font-size: 13px;
                padding: 8px 12px;
                border-top: 1px solid #CDD8EC;
            }}
        """)
        layout.addWidget(self.hint_lbl)

        # ── Input bar ─────────────────────────────────────────────────────
        input_bar = QWidget()
        input_bar.setStyleSheet("background-color: white;")
        input_layout = QHBoxLayout(input_bar)
        input_layout.setContentsMargins(14, 10, 14, 10)

        self.input = QTextEdit()
        self.input.setAcceptRichText(False)
        self.input.setPlaceholderText("Type your question…")
        self.input.setFixedHeight(80)
        self.input.setStyleSheet(f"""
            QTextEdit {{
                background-color: {C_INPUT_BG};
                color: #000000;
                border: 1px solid {C_DIVIDER};
                border-radius: 16px;
                padding: 10px;
                font-family: "{FONT_FAMILY}";
                font-size: 16px;
            }}
        """)
        self.input.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        self.input.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        self.input.installEventFilter(self)
        input_layout.addWidget(self.input, 1)

        self.send_btn = QPushButton("➤")
        self.send_btn.setFixedSize(50, 80)
        self.send_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {C_BLUE};
                color: white;
                border-radius: 16px;
                font-size: 22px;
            }}
            QPushButton:hover {{ background-color: {C_BLUE_HOV}; }}
        """)
        self.send_btn.clicked.connect(self._send)
        input_layout.addWidget(self.send_btn)

        layout.addWidget(input_bar)

        # ── Init agent ────────────────────────────────────────────────────
        if not self.cfg.get("openai_api_key", "").strip():
            QTimer.singleShot(200, lambda: self._open_settings(first=True))
        else:
            QTimer.singleShot(80, self._init_agent)

    # ── Event filter for Enter / Shift+Enter ────────────────────────────
    def eventFilter(self, obj, event):
        from PyQt6.QtCore import QEvent
        if obj is self.input and event.type() == QEvent.Type.KeyPress:
            if event.key() == Qt.Key.Key_Return and not (
                event.modifiers() & Qt.KeyboardModifier.ShiftModifier
            ):
                self._send()
                return True
        return super().eventFilter(obj, event)

    # ── Agent init ──────────────────────────────────────────────────────
    def _init_agent(self):
        key = self.cfg.get("openai_api_key", "").strip()
        if not key:
            return
        try:
            src_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            if src_dir not in sys.path:
                sys.path.insert(0, src_dir)
            from tax_form_agent.form_knowledge import FormKnowledge
            from tax_form_agent.llm_client import LLMClient
            from tax_form_agent.agent import TaxFormAgent

            fk = FormKnowledge(_data_path())
            llm = LLMClient(api_key=key, model="gpt-4o-mini")
            self.agent = TaxFormAgent(fk, llm)
            self.lang = self.cfg.get("language", "en")
            self.agent.set_lang(self.lang, self.tid)
            self.lang_btn.setText("DE" if self.lang == "en" else "EN")
            sec1 = fk.get_section(1)
            sec1_name = sec1.name if sec1 else "Allgemeine Angaben"
            self._update_breadcrumb(
                f"Section 1: {sec1_name}" if self.lang == "en"
                else f"Abschnitt 1: {sec1_name}"
            )
            self._add_bot(format_bot_html(self._welcome()))
        except Exception as e:
            self._add_system(
                f"Agent konnte nicht geladen werden: {e}" if self.lang == "de"
                else f"Failed to load agent: {e}"
            )

    def _welcome(self) -> str:
        if self.lang == "en":
            return (
                "Welcome! I will guide you through the Fragebogen zur steuerlichen "
                "Erfassung für Einzelunternehmen — the German tax registration form "
                "for sole proprietorships.\n\n"
                "The form has 23 sections covering your personal data, business "
                "details, tax options, and banking information. I'll explain each "
                "field, what to enter, and what to watch out for.\n\n"
                "You are currently in Section 1. To navigate, type a section "
                "number or its German name (e.g. 'Kleinunternehmer-Regelung', "
                "'Geburtsdatum')."
            )
        return (
            "Willkommen! Ich führe Sie durch den Fragebogen zur steuerlichen "
            "Erfassung für Einzelunternehmen.\n\n"
            "Das Formular umfasst 23 Abschnitte zu Ihren persönlichen Daten, "
            "Unternehmensangaben, Steueroptionen und Bankverbindung. Ich "
            "erkläre jedes Feld, was einzutragen ist und worauf Sie achten "
            "müssen.\n\n"
            "Sie befinden sich in Abschnitt 1. Zur Navigation geben Sie eine "
            "Abschnittsnummer oder den deutschen Namen ein "
            "(z.B. 'Kleinunternehmer-Regelung', 'Geburtsdatum')."
        )

    # ── Send/receive ────────────────────────────────────────────────────
    def _send(self):
        if not self.agent:
            self._add_system(
                "Bitte zuerst den API-Key einstellen." if self.lang == "de"
                else "Please set your API key first."
            )
            return
        text = self.input.toPlainText().strip()
        if not text:
            return
        self.input.clear()
        self._add_user(text)
        self.send_btn.setEnabled(False)
        threading.Thread(target=self._worker, args=(text,), daemon=True).start()

    def _worker(self, text: str):
        # Capture the generation counter at start. Reset / lang toggle / API
        # change bumps self._stream_gen — once that happens, this worker's
        # remaining chunks and final reply are dropped on the UI side.
        gen = self._stream_gen
        # Reset streaming state for this turn (used by _on_chunk on the UI thread).
        self._stream_bubble = None
        self._stream_buffer = ""
        self._stream_bc_extracted = False
        self._stream_update_pending = False
        try:
            reply = self.agent.chat(
                text,
                thread_id=self.tid,
                on_chunk=lambda c: self.signals.chunk_arrived.emit(gen, c),
            )
        except Exception as e:
            reply = self._format_chat_error(e)
            if "OpenAI API error 401" in str(e):
                self.signals.auth_failed.emit(gen)
        self.signals.reply_ready.emit(gen, reply)

    def _format_chat_error(self, e: Exception) -> str:
        """Map raw OpenAI/HTTP errors to a friendly localized message so users
        don't see a wall of JSON in the chat bubble (e.g. the 401 dump that
        prints the masked key and the api-keys URL)."""
        msg = str(e)
        is_de = self.lang == "de"
        if "OpenAI API error 401" in msg:
            return (
                "Der OpenAI-API-Schlüssel ist ungültig oder abgelaufen. "
                "Bitte öffnen Sie die Einstellungen (API-Button oben rechts) "
                "und tragen Sie einen gültigen Schlüssel ein."
                if is_de else
                "The OpenAI API key is invalid or has expired. Please open "
                "Settings (API button, top right) and enter a valid key."
            )
        if "OpenAI API error 429" in msg:
            return (
                "OpenAI lehnt die Anfrage ab: Limit erreicht oder kein "
                "Guthaben auf dem Konto. Bitte später erneut versuchen."
                if is_de else
                "OpenAI rejected the request: rate limit reached or no "
                "credit on the account. Please try again later."
            )
        if "OpenAI API error 5" in msg:
            return (
                "OpenAI-Server ist gerade nicht erreichbar. "
                "Bitte in ein paar Minuten erneut versuchen."
                if is_de else
                "OpenAI is currently unreachable. Please try again "
                "in a few minutes."
            )
        if "timed out" in msg.lower() or "timeout" in msg.lower():
            return (
                "Zeitüberschreitung bei der Anfrage. Bitte Internet prüfen "
                "und erneut versuchen."
                if is_de else
                "The request timed out. Please check your internet and try again."
            )
        return (
            f"Fehler bei der Anfrage: {type(e).__name__}."
            if is_de else
            f"Request failed: {type(e).__name__}."
        )

    def _on_auth_failed(self, gen: int):
        """Open the settings dialog after a 401 so the user can fix the key
        without hunting for the API button."""
        if gen != self._stream_gen:
            return
        QTimer.singleShot(400, lambda: self._open_settings(first=False))

    def _clean_for_streaming(self, text: str) -> str:
        """Apply the same transformations as _process_response so the streamed
        view matches the final view. Pulls the breadcrumb line into the top
        bar (once), removes the trailing nav tip, strips markdown bold."""
        # Pull breadcrumb out of the body (only once per stream)
        if text.startswith("📍"):
            if "\n" in text:
                first_line, rest = text.split("\n", 1)
                if not self._stream_bc_extracted:
                    self._update_breadcrumb(first_line.lstrip("📍 ").strip())
                    self._stream_bc_extracted = True
                text = rest.lstrip("\n")
            else:
                # Breadcrumb still arriving — nothing to display yet.
                return ""

        # Strip trailing 🧭 navigation tip (matches _process_response).
        text = self._strip_nav_tip(text)
        # Strip complete markdown bold (incomplete ones are left until the
        # closing ** arrives; the final pass cleans them up).
        text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)
        return text

    def _on_chunk(self, gen: int, chunk: str):
        """A new piece of the streaming reply has arrived. Append to the buffer
        and schedule a throttled UI flush — re-rendering the bubble on every
        single token at LLM rate (~50–100/sec) causes visible flicker."""
        if gen != self._stream_gen:
            return  # request was cancelled (reset / lang toggle / API change)
        self._stream_buffer += chunk
        if not self._stream_update_pending:
            self._stream_update_pending = True
            QTimer.singleShot(120, self._flush_stream_update)

    def _is_at_bottom(self) -> bool:
        """True if the viewport is currently at (or very close to) the bottom.
        Used to follow new content only when the user hasn't scrolled up."""
        bar = self.scroll.verticalScrollBar()
        return bar.value() >= bar.maximum() - 60

    def _flush_stream_update(self):
        """Apply the current stream buffer to the bubble. Fires at most every
        120 ms regardless of how many chunks arrive in between."""
        self._stream_update_pending = False
        if not self._stream_buffer:
            return
        display = self._clean_for_streaming(self._stream_buffer)
        if not display:
            return  # only breadcrumb so far, nothing visible yet

        was_at_bottom = self._is_at_bottom()
        try:
            if self._stream_bubble is None:
                self._stream_bubble = self._add_bot_streaming(display)
            else:
                self._stream_bubble.setUpdatesEnabled(False)
                self._stream_bubble.setHtml(self._format_streaming(display))
                self._stream_bubble.setUpdatesEnabled(True)
                self._snap_bot_bubble_height(self._stream_bubble)
        except RuntimeError:
            # Bubble's underlying C++ widget was deleted (e.g. by _clear_chat
            # after a Reset that raced this flush). Drop the update silently.
            self._stream_bubble = None
            self._stream_buffer = ""
            return
        if was_at_bottom:
            QTimer.singleShot(0, self._scroll_to_bottom)

    def _format_streaming(self, text: str) -> str:
        """HTML rendering for in-flight streamed text. Uses the same
        format_bot_html as the final pass so blue terms and bullets appear
        as soon as the relevant tokens arrive. Patterns spanning the cut
        will flicker briefly as more tokens stream in — acceptable trade-off
        for live-formatted output."""
        return format_bot_html(text, self._current_cursor_name())

    def _add_bot_streaming(self, initial_text: str):
        """Create an empty bot bubble that will be filled by chunks. Returns
        the bubble widget so subsequent chunks can update its content."""
        row = QWidget()
        row_layout = QHBoxLayout(row)
        row_layout.setContentsMargins(0, 0, 0, 0)
        bubble = BotBubble(self._format_streaming(initial_text))
        bubble.setProperty("bubble_role", "bot")
        # Pin full bot-width up front so streaming text wraps consistently
        # from the first chunk — without this, _reflow_bubbles would size
        # the bubble against the (very short) first chunk and lock the
        # stream into a thin column.
        bubble.setFixedWidth(int(self.width() * 0.70))
        self._snap_bot_bubble_height(bubble)
        row_layout.addWidget(bubble)
        row_layout.addStretch()
        self.chat_layout.addWidget(row)
        QTimer.singleShot(10, self._scroll_to_bottom)
        return bubble

    def _on_reply(self, gen: int, reply: str):
        if gen != self._stream_gen:
            # Worker finished a request that was already cancelled by the
            # user (Reset / lang toggle / API change). Drop the payload —
            # the cancelling action has already re-enabled send_btn and
            # rebuilt the chat state.
            return
        cleaned = self._process_response(reply)
        final_html = format_bot_html(cleaned, self._current_cursor_name())
        has_content = bool(re.sub(r'<[^>]+>|&nbsp;|\s', '', final_html))
        if self._stream_bubble is not None:
            # Streaming case — replace the in-progress bubble with the final
            # nicely-formatted HTML (blue terms, bullets, etc.). If the final
            # cleanup left the body empty (e.g. agent returned breadcrumb-only
            # after a skip-section personalization hint), keep whatever was
            # streamed rather than blanking the bubble.
            if has_content:
                self._stream_bubble.setHtml(final_html)
                self._snap_bot_bubble_height(self._stream_bubble)
            self._stream_bubble = None
            self._stream_buffer = ""
            QTimer.singleShot(0, self._reflow_bubbles)
            QTimer.singleShot(0, self._scroll_to_bottom)
        elif has_content:
            # Non-streamed path (agent returned without invoking on_chunk —
            # e.g. early-return paths like option-match, ack, "not found").
            self._add_bot(final_html)
        self.send_btn.setEnabled(True)

    def _current_cursor_name(self) -> str:
        """Last segment of the breadcrumb — current field/subsection name."""
        bc = getattr(self, "_bc_raw", "") or ""
        bc = bc.lstrip("📍 ").strip()
        for sep in ("→", "›", ">"):
            bc = bc.replace(f" {sep} ", "|SEP|").replace(sep, "|SEP|")
        parts = [p.strip() for p in bc.split("|SEP|") if p.strip()]
        return parts[-1] if parts else ""

    @staticmethod
    def _strip_nav_tip(text: str) -> str:
        """Drop the trailing 🧭 navigation tip (the LLM is prompted to append
        one). Use rfind, not regex with re.DOTALL — if the model accidentally
        emits 🧭 in the middle of a long answer, a greedy regex would chop
        the rest of the response. rfind handles only the *last* occurrence
        and only if it looks like a tail (≤ 400 chars after it)."""
        idx = text.rfind('🧭')
        if idx < 0:
            return text
        # Only treat it as the trailing nav tip if it's near the end.
        if len(text) - idx > 400:
            return text
        nl = text.rfind('\n', 0, idx)
        if nl >= 0:
            # 🧭 starts on its own line — strip from that line onward.
            return text[:nl + 1].rstrip()
        # 🧭 is on the first line of `text`. Preserve any body that precedes it
        # on the same line — without this guard, short replies whose body ends
        # up adjacent to the tip (no newline between) lose the whole body.
        return text[:idx].rstrip()

    def _process_response(self, raw: str) -> str:
        text = raw.strip()
        if text.startswith("📍"):
            lines = text.split("\n")
            self._update_breadcrumb(lines[0].lstrip("📍 ").strip())
            text = "\n".join(lines[1:]).lstrip("\n").strip()
        text = self._strip_nav_tip(text)
        text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)
        return text

    # ── Breadcrumb ──────────────────────────────────────────────────────
    def _update_breadcrumb(self, crumb: str):
        self._bc_raw = crumb
        # Normalize separators
        clean = crumb.lstrip("📍 ").strip()
        for sep in ("→", "›", ">"):
            clean = clean.replace(f" {sep} ", "|SEP|").replace(sep, "|SEP|")
        parts = [p.strip() for p in clean.split("|SEP|") if p.strip()]
        # Build HTML with clickable links
        segs = []
        for i, p in enumerate(parts):
            path = " > ".join(parts[:i + 1])
            is_last = i == len(parts) - 1
            is_hover = (path == self._bc_hover) and not is_last
            if is_last:
                color, decoration = "#1C1E21", "none"
            elif is_hover:
                color, decoration = C_BLUE, "underline"
            else:
                color, decoration = "#666", "none"
            segs.append(
                f'<a href="{_html_mod.escape(path, quote=True)}" '
                f'style="color:{color}; text-decoration:{decoration};">{_esc(p)}</a>'
            )
        sep = ' <span style="color:#C0C0C0">›</span> '
        self.breadcrumb_lbl.setText(sep.join(segs))

    def _on_breadcrumb_hover(self, link: str):
        self._bc_hover = link if link else None
        if link:
            self.breadcrumb_lbl.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        else:
            self.breadcrumb_lbl.unsetCursor()
        if getattr(self, "_bc_raw", None):
            self._update_breadcrumb(self._bc_raw)

    def _on_breadcrumb_click(self, path: str):
        if not self.agent:
            return
        parts = [p.strip() for p in path.split(">")]
        m = re.match(r'(?:Section|Abschnitt)\s+(\d+)', parts[0])
        if not m:
            return
        cmd = m.group(1) if len(parts) == 1 else " → ".join(parts)
        self._add_user(cmd)
        self.send_btn.setEnabled(False)
        threading.Thread(target=self._worker, args=(cmd,), daemon=True).start()

    # ── Chat rendering ──────────────────────────────────────────────────
    def _add_bot(self, html: str):
        row = QWidget()
        row_layout = QHBoxLayout(row)
        row_layout.setContentsMargins(0, 0, 0, 0)
        bubble = BotBubble(html)
        bubble.setProperty("bubble_role", "bot")
        # Size the bubble before adding it to the layout — otherwise QTextEdit
        # briefly takes its default (very large) sizeHint and the layout puts
        # the widget wherever fits, leading to a one-frame "centered" jump.
        bubble.setFixedWidth(int(self.width() * 0.70))
        self._snap_bot_bubble_height(bubble)
        row_layout.addWidget(bubble)
        row_layout.addStretch()
        self.chat_layout.addWidget(row)
        QTimer.singleShot(0, self._reflow_bubbles)
        QTimer.singleShot(10, self._scroll_to_bottom)

    def _add_user(self, text: str):
        row = QWidget()
        row_layout = QHBoxLayout(row)
        row_layout.setContentsMargins(0, 0, 0, 0)
        row_layout.addStretch()
        bubble = UserBubble(text)
        bubble.setProperty("bubble_role", "user")
        row_layout.addWidget(bubble)
        self.chat_layout.addWidget(row)
        QTimer.singleShot(0, self._reflow_bubbles)
        QTimer.singleShot(10, self._scroll_to_bottom)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        QTimer.singleShot(0, self._reflow_bubbles)

    def _iter_bubbles(self):
        """Yield (widget, role) for every chat bubble currently in the layout.
        Bot bubbles are QTextEdit instances; user bubbles are QLabel."""
        for i in range(self.chat_layout.count()):
            item = self.chat_layout.itemAt(i)
            widget = item.widget()
            if not widget:
                continue
            for child in widget.findChildren((BotBubble, UserBubble)):
                role = child.property("bubble_role")
                if role in ("bot", "user"):
                    yield child, role

    def _snap_bot_bubble_height(self, bubble):
        """Set a BotBubble's fixed height to exactly fit its current document
        at its current width. QTextEdit's document().size() reports the real
        rendered content size with documentMargin=0 — no quirky trailing
        space like QLabel's rich-text rendering had."""
        if bubble is None:
            return
        inner_w = bubble.width() - 2 * bubble.PADDING_H
        if inner_w <= 0:
            return
        bubble.document().setTextWidth(inner_w)
        bubble.setFixedHeight(bubble.content_height())

    def _reflow_bubbles(self):
        """Recompute widths AND heights for all chat bubbles. Called on
        resize, on bubble creation, and after streaming completes."""
        from PyQt6.QtGui import QFontMetrics
        w = self.width()
        for child, role in self._iter_bubbles():
            max_w = int(w * (0.70 if role == "bot" else 0.62))
            fm = QFontMetrics(child.font())
            # Strip HTML tags to estimate natural unwrapped line width.
            raw = child.toHtml() if isinstance(child, BotBubble) else child.text()
            plain = re.sub(r'<[^>]+>', '', raw)
            max_line_px = max(
                (fm.horizontalAdvance(ln) for ln in plain.split("\n")),
                default=0,
            )
            desired = min(max_line_px + 40, max_w)
            child.setMinimumHeight(0)
            child.setMaximumHeight(16777215)
            child.setFixedWidth(desired)
            if isinstance(child, BotBubble):
                self._snap_bot_bubble_height(child)
            else:
                # UserBubble (QLabel) — heightForWidth still works here.
                try:
                    h = child.heightForWidth(desired)
                    if h > 0:
                        child.setFixedHeight(h)
                except Exception:
                    pass

    def _add_system(self, text: str):
        self.chat_layout.addWidget(SysLabel(text))
        QTimer.singleShot(10, self._scroll_to_bottom)

    def _scroll_to_bottom(self):
        bar = self.scroll.verticalScrollBar()
        bar.setValue(bar.maximum())

    def _clear_chat(self):
        while self.chat_layout.count():
            item = self.chat_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def _cancel_in_flight(self):
        """Invalidate any worker that's currently streaming, so its remaining
        chunks/reply are dropped on arrival. Re-enable the send button — it
        was disabled by _send() and would otherwise stay grey until the
        (cancelled) worker eventually finishes."""
        self._stream_gen += 1
        self._stream_bubble = None
        self._stream_buffer = ""
        self._stream_update_pending = False
        self.send_btn.setEnabled(True)

    # ── Language ────────────────────────────────────────────────────────
    def _toggle_lang(self):
        if not self.agent:
            return
        self._cancel_in_flight()
        self.lang = "de" if self.lang == "en" else "en"
        self.agent.set_lang(self.lang, self.tid)
        self.cfg["language"] = self.lang
        save_config(self.cfg, self.cfg_path)
        self.lang_btn.setText("DE" if self.lang == "en" else "EN")
        self.hint_lbl.setText(HINT_EN if self.lang == "en" else HINT_DE)
        cur = getattr(self, "_bc_raw", "")
        if self.lang == "en":
            cur = cur.replace("Abschnitt", "Section")
        else:
            cur = cur.replace("Section", "Abschnitt")
        if cur:
            self._update_breadcrumb(cur)
        self._add_system(
            "Sprache: Deutsch ✓" if self.lang == "de" else "Language: English ✓"
        )

    # ── Reset ───────────────────────────────────────────────────────────
    def _reset_chat(self):
        if not self.agent:
            return
        self._cancel_in_flight()
        self.agent.reset(self.tid)
        self.agent.set_lang(self.lang, self.tid)
        self._clear_chat()
        fk = self.agent.fk
        sec1 = fk.get_section(1)
        sec1_name = sec1.name if sec1 else "Allgemeine Angaben"
        self._update_breadcrumb(
            f"Section 1: {sec1_name}" if self.lang == "en"
            else f"Abschnitt 1: {sec1_name}"
        )
        self._add_system("Gespräch zurückgesetzt" if self.lang == "de"
                         else "conversation reset")
        self._add_bot(format_bot_html(self._welcome()))

    # ── Settings ────────────────────────────────────────────────────────
    def _open_settings(self, first: bool = False):
        old_key = self.cfg.get("openai_api_key", "")
        dlg = SettingsDialog(self, self.cfg, first_launch=first, lang=self.lang)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            new_key = dlg.key()
            if new_key != old_key:
                self._cancel_in_flight()
                self.cfg["openai_api_key"] = new_key
                self.cfg.setdefault("model", "gpt-4o-mini")
                save_config(self.cfg, self.cfg_path)
                self.agent = None
                self._clear_chat()
                self._init_agent()
        elif first:
            # First launch and user cancelled — exit app
            self.close()


# ── Settings dialog ───────────────────────────────────────────────────────

class SettingsDialog(QDialog):
    def __init__(self, parent, cfg, first_launch=False, lang="en"):
        super().__init__(parent)
        is_de = lang == "de"
        self.setWindowTitle("API-Schlüssel" if is_de else "API Key")
        self.setFixedSize(500, 300)
        self.setStyleSheet("background-color: white;")
        if first_launch:
            self.setWindowModality(Qt.WindowModality.ApplicationModal)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 28, 28, 20)
        layout.setSpacing(8)

        title = QLabel("OpenAI API-Schlüssel" if is_de else "OpenAI API Key")
        title.setStyleSheet(
            f'font-family: "{FONT_FAMILY}"; font-size: 16px; font-weight: bold; color: #1C1E21;'
        )
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        sub = QLabel(
            "Lokal auf Ihrem Computer gespeichert, wird nicht weitergegeben."
            if is_de
            else "Saved locally on your computer, never shared."
        )
        sub.setStyleSheet(
            f'font-family: "{FONT_FAMILY}"; font-size: 13px; color: #888;'
        )
        sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sub.setWordWrap(True)
        layout.addWidget(sub)
        layout.addSpacing(8)

        self.entry = QLineEdit()
        self.entry.setText(cfg.get("openai_api_key", ""))
        self.entry.setEchoMode(QLineEdit.EchoMode.Password)
        self.entry.setPlaceholderText("sk-proj-...")
        self.entry.setFixedHeight(40)
        self.entry.setStyleSheet(f"""
            QLineEdit {{
                background-color: {C_INPUT_BG};
                border: 1px solid {C_DIVIDER};
                border-radius: 10px;
                padding: 0 12px;
                font-family: "{FONT_FAMILY}"; font-size: 14px;
            }}
        """)
        layout.addWidget(self.entry)

        self.show_chk = QCheckBox("Schlüssel anzeigen" if is_de else "Show key")
        self.show_chk.stateChanged.connect(
            lambda s: self.entry.setEchoMode(
                QLineEdit.EchoMode.Normal if s else QLineEdit.EchoMode.Password
            )
        )
        self.show_chk.setStyleSheet(
            f'font-family: "{FONT_FAMILY}"; font-size: 13px;'
        )
        layout.addWidget(self.show_chk, alignment=Qt.AlignmentFlag.AlignCenter)

        self.status_lbl = QLabel("")
        self.status_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_lbl.setStyleSheet(
            f'font-family: "{FONT_FAMILY}"; font-size: 13px; color: #E53E3E;'
        )
        self.status_lbl.setWordWrap(True)
        layout.addWidget(self.status_lbl)

        layout.addSpacing(12)

        self.save_btn = QPushButton("Speichern" if is_de else "Save")
        self._save_label_default = "Speichern" if is_de else "Save"
        self._save_label_checking = "Prüfe…" if is_de else "Checking…"
        self.save_btn.setFixedSize(140, 44)
        self.save_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {C_BLUE};
                color: white;
                border-radius: 22px;
                font-family: "{FONT_FAMILY}"; font-size: 15px; font-weight: bold;
            }}
            QPushButton:hover {{ background-color: {C_BLUE_HOV}; }}
            QPushButton:disabled {{ background-color: #9FB5D8; }}
        """)
        self.save_btn.clicked.connect(self._save)
        layout.addWidget(self.save_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        self._is_de = is_de

    def _validate_key(self, key: str) -> tuple[bool, str]:
        """Hit OpenAI /v1/models to verify auth. Returns (ok, error_message)."""
        # OpenAI keys are pure ASCII (sk-… + alphanumerics). Reject non-ASCII
        # locally so we can give a clear message instead of a network crash.
        if not key.isascii():
            return False, (
                "Unzulässige Zeichen. Ein OpenAI-Schlüssel beginnt mit "
                "„sk-…“ und enthält nur lateinische Buchstaben und Ziffern."
                if self._is_de else
                "Invalid characters. An OpenAI key starts with “sk-…” and "
                "contains only Latin letters and digits."
            )

        import socket
        from tax_form_agent.llm_client import open_https_resilient
        try:
            conn = open_https_resilient("api.openai.com", timeout=12)
            try:
                conn.request("GET", "/v1/models",
                             headers={"Authorization": f"Bearer {key}"})
                resp = conn.getresponse()
                resp.read()
                status = resp.status
            finally:
                conn.close()
        except (socket.gaierror, socket.timeout, OSError):
            return False, (
                "Keine Verbindung zu OpenAI. Internet prüfen und erneut versuchen."
                if self._is_de else
                "Couldn't reach OpenAI. Check your internet and try again."
            )
        except Exception as e:
            return False, (
                f"Unerwarteter Fehler: {type(e).__name__}."
                if self._is_de else
                f"Unexpected error: {type(e).__name__}."
            )

        if status == 200:
            return True, ""
        if status == 401:
            return False, (
                "OpenAI lehnt diesen Schlüssel ab. Bitte prüfen Sie, ob Sie "
                "ihn komplett kopiert haben."
                if self._is_de else
                "OpenAI rejected this key. Make sure you copied it in full."
            )
        if status == 429:
            return False, (
                "Schlüssel gültig, aber kein Guthaben auf dem OpenAI-Konto."
                if self._is_de else
                "Key is valid, but your OpenAI account has no credit."
            )
        return False, (
            f"Fehler beim Prüfen (HTTP {status}). Bitte später erneut versuchen."
            if self._is_de else
            f"Check failed (HTTP {status}). Please try again later."
        )

    def _save(self):
        key = self.entry.text().strip()
        if not key:
            self.status_lbl.setText(
                "Bitte API-Schlüssel eingeben." if self._is_de
                else "Please enter an API key."
            )
            return

        self.save_btn.setEnabled(False)
        self.save_btn.setText(self._save_label_checking)
        self.status_lbl.setText("")
        QApplication.processEvents()

        ok, err = self._validate_key(key)

        self.save_btn.setEnabled(True)
        self.save_btn.setText(self._save_label_default)

        if not ok:
            self.status_lbl.setText(err)
            return
        self.accept()

    def key(self) -> str:
        return self.entry.text().strip()


# ── Entry point ───────────────────────────────────────────────────────────

def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setApplicationName("Bruno")
    app.setStyleSheet(f"""
        QMenu {{
            background-color: #FFFFFF;
            border: 1px solid {C_DIVIDER};
            border-radius: 10px;
            padding: 6px;
            font-family: "{FONT_FAMILY}";
            font-size: 14px;
            color: {C_BOT_FG};
        }}
        QMenu::item {{
            background-color: transparent;
            padding: 8px 18px 8px 14px;
            border-radius: 6px;
            margin: 1px;
        }}
        QMenu::item:selected {{
            background-color: {C_HINT_BG};
            color: {C_HINT_FG};
        }}
        QMenu::item:disabled {{
            color: {C_SYS_FG};
        }}
        QMenu::separator {{
            height: 1px;
            background: {C_DIVIDER};
            margin: 4px 8px;
        }}
    """)
    # Set app icon
    root = _app_dir() if getattr(sys, '_MEIPASS', None) else \
           os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    for icon_name in ("icon.icns", "icon.ico", "icon.png"):
        p = os.path.join(root, icon_name)
        if os.path.exists(p):
            from PyQt6.QtGui import QIcon
            app.setWindowIcon(QIcon(p))
            break
    _install_fonts()
    win = ChatWindow()
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
