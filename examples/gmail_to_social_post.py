#!/usr/bin/env python3
"""Example: Fetch Gmail emails and post summary to Discord.

@llm-type example.graph.gmail_to_social
@llm-does demonstrate APINode with Gmail and Discord drivers in a graph

This example shows:
1. Fetching unread Gmail messages via GmailDriver
2. Processing emails (could add LLM summarization)
3. Posting summary to Discord via DiscordDriver

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
from libs.python.drivers.social.discord import DiscordDriver
from libs.python.graph import APINode, Graph, GraphExecutionResult, GraphExecutor


def _display_results(result: GraphExecutionResult) -> None:
    """Display execution results with reduced nesting."""
    print("\n[4] Execution complete:")
    print(f"    Success: {result.success}")
    print(f"    Execution order: {result.execution_order}")

    for node_id, node_result in result.node_results.items():
        print(f"\n    Node: {node_id}")
        print(f"      Success: {node_result.success}")

        if not node_result.success:
            print(f"      Error: {node_result.error}")
            continue

        data = node_result.output.get("data", {})
        if "emails" in data:
            emails = data["emails"]
            print(f"      Fetched {len(emails)} emails")
            for email in emails[:3]:
                print(f"        - {email.get('subject', 'No subject')}")
        elif "id" in data:
            print(f"      Posted message: {data['id']}")


async def main() -> None:
    """Execute Gmail → Discord workflow."""
    print("=" * 60)
    print("Gmail to Social Media Post Example")
    print("=" * 60)

    # Step 1: Register drivers
    print("\n[1] Registering drivers...")
    registry = get_global_registry()

    gmail_driver = GmailDriver()
    discord_driver = DiscordDriver()

    registry.register("google.gmail", gmail_driver)
    registry.register("social.discord", discord_driver)

    print(f"    Registered: {registry.list_namespaces()}")

    # Step 2: Build graph
    print("\n[2] Building graph...")
    graph = Graph()

    # Node 1: Fetch unread Gmail messages
    gmail_node = APINode(
        node_id="fetch_emails",
        driver_namespace="google.gmail",
        operation="list_unread",
        params={"limit": 5},
    )
    graph.add_node(gmail_node)

    # Node 2: Post to Discord (in real workflow, would add LLM summarization between)
    discord_node = APINode(
        node_id="post_to_discord",
        driver_namespace="social.discord",
        operation="post_message",
        params={
            "channel_id": "YOUR_CHANNEL_ID",  # Replace with actual channel ID
            "content": "Email summary placeholder",  # Would be generated from emails
        },
    )
    graph.add_node(discord_node)

    # Connect nodes (in real workflow, would add processing node between)
    graph.add_edge("fetch_emails", "post_to_discord")

    print(f"    Nodes: {list(graph.nodes.keys())}")
    print(f"    Edges: {graph.edges}")

    # Step 3: Execute graph
    print("\n[3] Executing graph...")
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
