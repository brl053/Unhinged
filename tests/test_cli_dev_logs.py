"""Tests for ``unhinged dev logs`` CLI commands."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from click.testing import CliRunner

from cli.commands.dev import dev


def _runner() -> CliRunner:
    return CliRunner()


def test_dev_logs_no_events():
    runner = _runner()

    with patch("cli.commands.dev.dump_all_events", return_value=[]):
        result = runner.invoke(dev, ["logs"])

    assert result.exit_code == 0
    assert "No events found" in result.output


def test_dev_logs_dumps_events_as_json():
    runner = _runner()
    events = [
        {"service_id": "svc", "event_type": "e1"},
        {"service_id": "svc", "event_type": "e2"},
    ]

    with patch("cli.commands.dev.dump_all_events", return_value=events):
        result = runner.invoke(dev, ["logs"])

    assert result.exit_code == 0
    # Separator lines
    assert result.output.count("---") == 2
    assert '"event_type": "e1"' in result.output
    assert '"event_type": "e2"' in result.output


def test_dev_logs_clear_uses_clear_all_events():
    runner = _runner()
    clear_mock = MagicMock(return_value=True)

    with patch("cli.commands.dev.clear_all_events", clear_mock):
        result = runner.invoke(dev, ["logs", "clear"])

    assert result.exit_code == 0
    clear_mock.assert_called_once_with()
    assert "Cleared all events" in result.output
