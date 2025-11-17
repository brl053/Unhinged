"""Tests for prompt orchestration and Jinja2 rendering.

@llm-type test-prompt-orchestration
@llm-does Tests UnhingedPromptRenderer template rendering functionality
"""

from pathlib import Path

import pytest

from libs.python.prompt_orchestration import UnhingedPromptRenderer


class TestUnhingedPromptRenderer:
    """Test suite for UnhingedPromptRenderer."""

    @pytest.fixture
    def renderer(self) -> UnhingedPromptRenderer:
        """Create renderer instance."""
        return UnhingedPromptRenderer()

    def test_renderer_initialization(self, renderer: UnhingedPromptRenderer) -> None:
        """Test renderer initializes with correct prompts directory."""
        assert renderer.prompts_dir.exists()
        assert renderer.prompts_dir.name == "prompts"

    def test_list_templates(self, renderer: UnhingedPromptRenderer) -> None:
        """Test listing available templates."""
        templates = renderer.list_templates()
        assert len(templates) > 0
        assert any("memorandum.j2" in t for t in templates)
        assert any("headers.j2" in t for t in templates)

    def test_render_simple_template(self, renderer: UnhingedPromptRenderer) -> None:
        """Test rendering a simple template with context."""
        context = {
            "to_recipient": "Chief of Science",
            "from_sender": "Test Division",
            "date": "16 November 2025",
            "subject": "Test Memorandum",
        }
        result = renderer.render_template("fragments/headers.j2", context)

        assert "MEMORANDUM" in result
        assert "Chief of Science" in result
        assert "Test Division" in result
        assert "Test Memorandum" in result

    def test_render_memo_full(self, renderer: UnhingedPromptRenderer) -> None:
        """Test rendering a complete memorandum."""
        result = renderer.render_memo(
            to_recipient="Chief of Science",
            from_sender="Systems Architecture Division",
            subject="Test Implementation",
            executive_summary="This is a test memorandum.",
            sections=[
                {
                    "title": "Implementation Status",
                    "content": "All components complete.",
                    "list_items": ["Item 1", "Item 2"],
                }
            ],
            findings=[
                {
                    "title": "Finding 1",
                    "content": "This is a test finding.",
                }
            ],
            recommendations=["Recommendation 1", "Recommendation 2"],
            disposition="Approved",
            distribution="Test Team",
            classification="Internal Use",
            tracking="TEST-001",
        )

        assert "MEMORANDUM" in result
        assert "Chief of Science" in result
        assert "EXECUTIVE SUMMARY" in result
        assert "This is a test memorandum." in result
        assert "IMPLEMENTATION STATUS" in result
        assert "Item 1" in result
        assert "FINDINGS" in result
        assert "RECOMMENDATIONS" in result
        assert "Approved" in result
        assert "TEST-001" in result

    def test_render_memo_minimal(self, renderer: UnhingedPromptRenderer) -> None:
        """Test rendering memorandum with minimal fields."""
        result = renderer.render_memo(
            to_recipient="Recipient",
            from_sender="Sender",
            subject="Subject",
            executive_summary="Summary",
        )

        assert "MEMORANDUM" in result
        assert "Recipient" in result
        assert "Sender" in result
        assert "Summary" in result

    def test_template_with_variables(self, renderer: UnhingedPromptRenderer) -> None:
        """Test template rendering with various variable types."""
        context = {
            "to_recipient": "Test",
            "from_sender": "Test",
            "date": "16 November 2025",
            "subject": "Test",
            "key_metrics": ["Metric 1", "Metric 2", "Metric 3"],
            "critical_findings": ["Finding A", "Finding B"],
        }
        result = renderer.render_template("fragments/executive.j2", context)

        assert "EXECUTIVE SUMMARY" in result
        assert "Metric 1" in result
        assert "Finding A" in result

    def test_invalid_template_raises_error(self, renderer: UnhingedPromptRenderer) -> None:
        """Test that invalid template raises error."""
        with pytest.raises(Exception):
            renderer.render_template("nonexistent/template.j2", {})

    def test_render_with_empty_sections(self, renderer: UnhingedPromptRenderer) -> None:
        """Test rendering with empty sections list."""
        result = renderer.render_memo(
            to_recipient="Test",
            from_sender="Test",
            subject="Test",
            executive_summary="Test",
            sections=[],
        )

        assert "MEMORANDUM" in result
        assert "Test" in result
