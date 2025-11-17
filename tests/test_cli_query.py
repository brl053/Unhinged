"""Tests for unhinged query CLI command."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
import yaml
from click.testing import CliRunner

from cli.commands.query import query


@pytest.fixture
def cli_runner() -> CliRunner:
    """Create CLI runner for testing."""

    return CliRunner()


def test_query_plan_only_yaml_output(cli_runner: CliRunner) -> None:
    """Plan-only query produces YAML with plan structure."""

    result = cli_runner.invoke(query, ["my headphone volume is too low"])

    assert result.exit_code == 0
    data = yaml.safe_load(result.output)

    assert isinstance(data, dict)
    assert data["query"]
    assert data["plan"]["domain"] == "audio/headphone_volume"
    assert data["plan"]["intent"] == "volume_low"


def test_query_execute_dry_run_json_output(cli_runner: CliRunner) -> None:
    """Dry-run execution compiles graph but does not run commands."""

    result = cli_runner.invoke(
        query,
        ["--execute", "--dry-run", "--output", "json", "headphone volume too low"],
    )

    assert result.exit_code == 0

    # Strip log lines (which are printed before the JSON document) and
    # decode only the JSON payload starting at the first ``{``.
    output = result.output
    json_start = output.find("{")
    assert json_start != -1
    data = json.loads(output[json_start:])

    assert data["plan"]["domain"] == "audio/headphone_volume"
    execution = data.get("execution")
    assert execution
    assert execution["dry_run"] is True
    assert "graph" in execution
    graph = execution["graph"]


def test_query_browser_audio_volume_supported(cli_runner: CliRunner) -> None:
    """Browser/system audio volume queries are supported in v1."""

    query_text = "why is my audio low from youtube and the browser? might be all apps idk"
    result = cli_runner.invoke(query, [query_text])

    assert result.exit_code == 0
    data = yaml.safe_load(result.output)
    assert data["plan"]["domain"] == "audio/system_volume"
    assert data["plan"]["intent"] == "volume_low"


def test_query_unsupported_intent_returns_error(cli_runner: CliRunner) -> None:
    """Non-audio queries are rejected in v1."""

    result = cli_runner.invoke(query, ["deploy my app to production"])

    assert result.exit_code != 0
    assert "Only audio volume diagnostics" in result.output
