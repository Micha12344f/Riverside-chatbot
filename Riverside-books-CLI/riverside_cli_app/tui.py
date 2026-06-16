from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from textual import on, work
from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical, VerticalScroll
from textual.message import Message
from textual.widgets import Input, Label, Static

from .chatbot import FALLBACK_MESSAGE, build_matcher
from .data import load_faqs


BOOK_FRAMES = [
    " .---.  .---.\n |   |  |   |\n |===|  |===|\n '---'  '---'",
    " .---.  .---.  .--.  .---.\n |   |  |===|  |  |  |   |\n |===|  |   |  |  |  |---|\n |   |  |===|  |==|  |   |\n '---'  '---'  '--'  '---'",
    ".---.  .---.  .--.  .---.  .---.\n|   |  |===|  |  |  |   |  |   |\n|===|  |   |  |  |  |---|  |===|\n|   |  |===|  |==|  |   |  |   |\n|---|  |   |  |  |  |---|  |---|\n|   |  |===|  |  |  |   |  |   |\n|===|  |   |  |==|  |---|  |===|\n'---'  '---'  '--'  '---'  '---'\n==================================",
]


class UserBubble(Static):
    BORDER_TITLE = " You "

    def __init__(self, text: str = "") -> None:
        super().__init__(text, markup=False)


class BotBubble(Static):
    BORDER_TITLE = " Riverside "

    def __init__(self, text: str = "") -> None:
        super().__init__(text, markup=False)


@dataclass(frozen=True)
class PendingResponse:
    bubble: BotBubble
    row: Container


class AnswerReady(Message):
    def __init__(
        self,
        pending: PendingResponse,
        answer: str,
        used_fallback: bool,
    ) -> None:
        self.pending = pending
        self.answer = answer
        self.used_fallback = used_fallback
        super().__init__()


class RiversideBooksApp(App[None]):
    CSS_PATH = "tui.tcss"
    TITLE = "Riverside Books"
    SUB_TITLE = "Chat UI"
    AUTO_FOCUS = "Input"
    BINDINGS = [
        ("ctrl+c", "quit", "Quit"),
        ("ctrl+l", "clear_chat", "Clear"),
        ("f2", "toggle_mode", "Mode"),
    ]

    def __init__(
        self,
        *,
        faq_path: Path | None = None,
        debug: bool = False,
        lexical_only: bool = False,
    ) -> None:
        super().__init__()
        self.faq_path = faq_path
        self.debug_mode = debug
        self.lexical_only = lexical_only
        self.faqs = load_faqs(faq_path)
        self.matcher = build_matcher(
            debug=self.debug_mode,
            lexical_only=self.lexical_only,
            logger=self._capture_debug_message,
        )
        self._frame_index = 0

    def compose(self) -> ComposeResult:
        yield Vertical(
            Horizontal(
                Static(id="corner-book"),
                Vertical(
                    Label("Riverside Books", id="app-title"),
                    Label("Simple bookshop help in your terminal", id="app-subtitle"),
                    id="title-block",
                ),
                id="top-row",
            ),
            VerticalScroll(id="chat-view"),
            Label(id="status-line"),
            Container(
                Input(placeholder="Ask Riverside Books a question...", id="question-input"),
                id="composer",
            ),
            id="screen-shell",
        )

    async def on_mount(self) -> None:
        self._render_book()
        self.set_timer(0.16, self._advance_book_animation)
        self.set_timer(0.32, self._advance_book_animation)
        await self._reset_chat()
        self._set_status("Ready")

    def _render_book(self) -> None:
        self.query_one("#corner-book", Static).update(BOOK_FRAMES[self._frame_index])

    def _advance_book_animation(self) -> None:
        self._frame_index = min(self._frame_index + 1, len(BOOK_FRAMES) - 1)
        self._render_book()

    def _mode_label(self) -> str:
        return "lexical only" if self.lexical_only else "semantic"

    def _set_status(self, message: str) -> None:
        self.query_one("#status-line", Label).update(message)

    async def _reset_chat(self) -> None:
        chat_view = self.query_one("#chat-view", VerticalScroll)
        await chat_view.remove_children()
        await self._mount_bot_message(
            "Welcome to Riverside Books.\n\n"
            "Ask about opening hours, parking, gift vouchers, click and collect, or the cafe.\n\n"
            f"{len(self.faqs)} FAQs loaded. Mode: {self._mode_label()}."
        )

    async def _mount_user_message(self, text: str) -> None:
        chat_view = self.query_one("#chat-view", VerticalScroll)
        bubble = UserBubble(text)
        row = Container(bubble, classes="message-row user-row")
        await chat_view.mount(row)
        row.anchor()

    async def _mount_bot_message(self, text: str, *, pending: bool = False) -> PendingResponse:
        chat_view = self.query_one("#chat-view", VerticalScroll)
        bubble = BotBubble(text)
        if pending:
            bubble.add_class("pending")
        row = Container(bubble, classes="message-row bot-row")
        await chat_view.mount(row)
        row.anchor()
        return PendingResponse(bubble=bubble, row=row)

    def _capture_debug_message(self, message: str) -> None:
        if not self.debug_mode:
            return
        self.call_from_thread(self._set_status, f"Debug: {message}")

    @on(Input.Submitted, "#question-input")
    async def handle_submit(self, event: Input.Submitted) -> None:
        question = event.value.strip()
        if not question:
            self._set_status("Type a question first.")
            return

        event.input.value = ""
        event.input.disabled = True
        await self._mount_user_message(question)
        pending = await self._mount_bot_message("Looking that up...", pending=True)
        self._set_status("Thinking...")
        self.answer_question(question, pending)

    @work(thread=True)
    def answer_question(self, question: str, pending: PendingResponse) -> None:
        result = self.matcher.match(question, self.faqs)
        if result is None:
            self.post_message(AnswerReady(pending, FALLBACK_MESSAGE, False))
            return
        self.post_message(AnswerReady(pending, result.faq.answer, result.used_fallback))

    @on(AnswerReady)
    def handle_answer_ready(self, event: AnswerReady) -> None:
        event.pending.bubble.remove_class("pending")
        event.pending.bubble.update(event.answer)
        if event.used_fallback:
            event.pending.bubble.border_subtitle = " fallback "
        else:
            event.pending.bubble.border_subtitle = ""
        event.pending.row.anchor()
        input_widget = self.query_one("#question-input", Input)
        input_widget.disabled = False
        input_widget.focus()
        self._set_status("Ready")

    async def action_clear_chat(self) -> None:
        await self._reset_chat()
        self._set_status("Ready")

    def action_toggle_mode(self) -> None:
        self.lexical_only = not self.lexical_only
        self.matcher = build_matcher(
            debug=self.debug_mode,
            lexical_only=self.lexical_only,
            logger=self._capture_debug_message,
        )
        self._set_status(f"Matcher mode changed to {self._mode_label()}.")


def run_tui(
    *,
    faq_path: Path | None = None,
    debug: bool = False,
    lexical_only: bool = False,
) -> int:
    app = RiversideBooksApp(
        faq_path=faq_path,
        debug=debug,
        lexical_only=lexical_only,
    )
    app.run()
    return 0
