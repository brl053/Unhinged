#!/usr/bin/env python3
"""Example: Fetch Gmail emails with time filtering.

@llm-type example.graph.gmail_fetch
@llm-does demonstrate APINode with Gmail driver and time-based queries

This example shows:
1. Fetching unread Gmail messages via GmailDriver
2. Time-based filtering (last 24h, 48h, etc.)
3. Processing email results

Usage:
    python examples/gmail_to_social_post.py
"""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

# Add project root to path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from libs.python.drivers.base import get_global_registry
from libs.python.drivers.google.gmail import GmailDriver
from libs.python.graph import APINode, Graph, GraphExecutionResult, GraphExecutor


def _display_results(result: GraphExecutionResult) -> None:
    """Display execution results."""
    print("\n[3] Execution complete:")
    print(f"    Success: {result.success}")

    for node_id, node_result in result.node_results.items():
        print(f"\n    Node: {node_id}")
        print(f"      Success: {node_result.success}")

        if not node_result.success:
            print(f"      Error: {node_result.error}")
            continue

        data = node_result.output.get("data", {})
        if "emails" in data:
            emails = data["emails"]
            print(f"      Fetched {len(emails)} emails from last 24 hours:")
            for email in emails:
                print(f"        - {email.get('subject', 'No subject')}")
                print(f"          From: {email.get('from', 'Unknown')}")
                print(f"          Date: {email.get('date', 'Unknown')}")
                print()


async def main() -> None:
    """Execute Gmail fetch workflow."""
    print("=" * 60)
    print("Gmail Fetch Example - Last 24 Hours")
    print("=" * 60)

    # Step 1: Register drivers
    print("\n[1] Registering drivers...")
    registry = get_global_registry()

    gmail_driver = GmailDriver()
    registry.register("google.gmail", gmail_driver)

    print(f"    Registered: {registry.list_namespaces()}")

    # Step 2: Build graph
    print("\n[2] Building graph...")
    graph = Graph()

    # Fetch unread emails from last 24 hours
    gmail_node = APINode(
        node_id="fetch_emails",
        driver_namespace="google.gmail",
        operation="list_unread",
        params={
            "limit": 10,
            "after_days": 1,  # Last 24 hours
        },
    )
    graph.add_node(gmail_node)

    print(f"    Nodes: {list(graph.nodes.keys())}")
    print(f"    Edges: {graph.edges}")

    # Step 3: Execute graph
    print("\n[2] Executing graph...")
    executor = GraphExecutor()

    try:
        result = await executor.execute(graph)
        _display_results(result)
    except Exception as exc:
        print(f"\n[!] Execution failed: {exc}")
        import traceback

        traceback.print_exc()

    print("\n" + "=" * 60)
    print("Example complete")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
