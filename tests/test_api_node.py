"""Tests for the APINode graph node with driver registry.

@llm-type test.graph.api_node
@llm-does unit tests for APINode execution with mock drivers
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, cast
from unittest.mock import AsyncMock, patch

import pytest

try:
    import libs  # type: ignore[import-not-found]
except ModuleNotFoundError:  # pragma: no cover - defensive path setup
    ROOT = Path(__file__).resolve().parents[1]
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    import libs  # type: ignore[import-not-found]  # noqa: F401

from libs.python.drivers.base import Driver, DriverCapability, get_global_registry
from libs.python.graph import APINode


class MockDriver(Driver):
    """Mock driver for testing."""

    def __init__(self, driver_id: str) -> None:
        super().__init__(driver_id)
        self.execute_mock = AsyncMock()

    def get_capabilities(self) -> list[DriverCapability]:
        return [DriverCapability.READ, DriverCapability.WRITE]

    async def execute(
        self,
        operation: str,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        return cast(dict[str, Any], await self.execute_mock(operation, params))


@pytest.mark.asyncio
async def test_api_node_executes_driver_operation() -> None:
    """APINode retrieves driver from registry and executes operation."""
    registry = get_global_registry()

    # Register mock driver
    mock_driver = MockDriver("test.service")
    mock_driver.execute_mock.return_value = {
        "success": True,
        "data": {"result": "operation_completed"},
    }
    registry.register("test.service", mock_driver)

    # Create and execute APINode
    node = APINode(
        node_id="api_test",
        driver_namespace="test.service",
        operation="test_operation",
        params={"param1": "value1"},
    )

    result = await node.execute()

    # Verify driver was called with correct params
    mock_driver.execute_mock.assert_awaited_once_with("test_operation", {"param1": "value1"})
    assert result["success"] is True
    assert result["data"]["result"] == "operation_completed"


@pytest.mark.asyncio
async def test_api_node_merges_input_data_params() -> None:
    """APINode merges input_data params with node params."""
    registry = get_global_registry()

    mock_driver = MockDriver("test.merge")
    mock_driver.execute_mock.return_value = {"success": True, "data": {}}
    registry.register("test.merge", mock_driver)

    node = APINode(
        node_id="merge_test",
        driver_namespace="test.merge",
        operation="merge_op",
        params={"base": "value", "override": "original"},
    )

    # Execute with input_data that overrides one param
    result = await node.execute(input_data={"params": {"override": "new", "extra": "added"}})

    # Verify merged params
    mock_driver.execute_mock.assert_awaited_once_with(
        "merge_op",
        {"base": "value", "override": "new", "extra": "added"},
    )
    assert result["success"] is True


@pytest.mark.asyncio
async def test_api_node_handles_missing_driver() -> None:
    """APINode returns error when driver not registered."""
    node = APINode(
        node_id="missing_test",
        driver_namespace="nonexistent.driver",
        operation="any_op",
    )

    result = await node.execute()

    assert result["success"] is False
    assert "not registered" in result["error"]


@pytest.mark.asyncio
async def test_api_node_handles_driver_error() -> None:
    """APINode surfaces driver errors as failed node output."""
    from libs.python.drivers.base import DriverError

    registry = get_global_registry()

    mock_driver = MockDriver("test.error")
    mock_driver.execute_mock.side_effect = DriverError("driver failed", status_code=500, driver_name="test.error")
    registry.register("test.error", mock_driver)

    node = APINode(
        node_id="error_test",
        driver_namespace="test.error",
        operation="fail_op",
    )

    result = await node.execute()

    assert result["success"] is False
    assert "driver failed" in result["error"]
