"""Step-based wizard flow for multi-step input.

Used by graph build command to collect nodes and edges.
Emits CDC events for session audit when context provided.
"""

from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

from rich.panel import Panel
from rich.prompt import Prompt

from cli.tui.console import console


@dataclass
class WizardStep:
    """Single step in a wizard flow.

    Attributes:
        name: Step identifier.
        title: Display title for the step.
        prompt: Question to ask the user.
        validator: Optional function to validate input. Returns error string or None.
        transformer: Optional function to transform raw input before storing.
        required: Whether the step requires non-empty input.
        default: Default value if user presses enter.
    """

    name: str
    title: str
    prompt: str
    validator: Callable[[str], str | None] | None = None
    transformer: Callable[[str], Any] | None = None
    required: bool = True
    default: str = ""


@dataclass
class WizardResult:
    """Result of wizard completion."""

    completed: bool
    data: dict[str, Any] = field(default_factory=dict)
    cancelled_at: str | None = None


class Wizard:
    """Multi-step wizard with back/next/cancel navigation.

    Usage:
        wizard = Wizard("Create Graph")
        wizard.add_step(WizardStep("name", "Graph Name", "Enter name:"))
        wizard.add_step(WizardStep("desc", "Description", "Enter description:", required=False))
        result = wizard.run()
        if result.completed:
            print(result.data)
    """

    def __init__(self, title: str, *, session_context: Any = None) -> None:
        """Initialize wizard.

        Args:
            title: Wizard title displayed at top.
            session_context: Optional SessionContext for CDC event emission.
        """
        self.title = title
        self.steps: list[WizardStep] = []
        self.context = session_context

    def add_step(self, step: WizardStep) -> None:
        """Add a step to the wizard."""
        self.steps.append(step)

    def _emit(self, event_type: str, data: dict[str, Any]) -> None:
        """Emit CDC event if context available."""
        if self.context is None:
            return
        try:
            from libs.python.graph.context import CDCEventType

            cdc_type = getattr(CDCEventType, event_type.upper(), CDCEventType.MSG_SYSTEM)
            self.context.emit(cdc_type, data)
        except (ImportError, AttributeError):
            pass

    def _display_header(self) -> None:
        """Display wizard header."""
        console.print()
        console.print(Panel(self.title, style="action.primary"))
        console.print()
        console.print("[text.secondary]Commands: [b]back[/b], [b]cancel[/b], or enter value[/text.secondary]")
        console.print()

    def _validate_response(self, step: WizardStep, response: str) -> str | None:
        """Validate step response. Returns error message or None if valid."""
        if step.required and not response:
            return "This field is required"
        if step.validator:
            return step.validator(response)
        return None

    def _handle_back(self, current: int) -> int:
        """Handle back navigation. Returns new step index."""
        if current > 0:
            return current - 1
        console.print("[warning]Already at first step[/warning]")
        return current

    def _process_step(self, step: WizardStep, current: int, data: dict[str, Any]) -> tuple[int, bool]:
        """Process a single step. Returns (new_index, should_continue)."""
        step_num = f"[{current + 1}/{len(self.steps)}]"
        console.print(f"\n{step_num} [highlight]{step.title}[/highlight]")

        prompt_text = step.prompt + (f" [{step.default}]" if step.default else "")
        response: str = Prompt.ask(prompt_text, console=console, default=step.default)
        response = response.strip()

        if response.lower() == "cancel":
            return (-1, False)  # Signal cancellation

        if response.lower() == "back":
            return (self._handle_back(current), True)

        error = self._validate_response(step, response)
        if error:
            console.print(f"[error]{error}[/error]")
            return (current, True)

        value = step.transformer(response) if step.transformer else response
        data[step.name] = value
        self._emit("msg_system", {"text": f"Step {step.name}: {value}"})
        return (current + 1, True)

    def run(self) -> WizardResult:
        """Execute the wizard flow.

        Returns:
            WizardResult with completion status and collected data.
        """
        data: dict[str, Any] = {}
        current = 0

        self._display_header()
        self._emit("msg_system", {"text": f"Wizard started: {self.title}"})

        while current < len(self.steps):
            step = self.steps[current]
            new_idx, should_continue = self._process_step(step, current, data)

            if not should_continue and new_idx == -1:
                self._emit("msg_system", {"text": f"Wizard cancelled at step: {step.name}"})
                return WizardResult(completed=False, data=data, cancelled_at=step.name)

            current = new_idx

        self._emit("msg_system", {"text": f"Wizard completed: {self.title}"})
        return WizardResult(completed=True, data=data)
