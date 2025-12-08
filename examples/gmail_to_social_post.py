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

from libs.python.drivers.base import get_global_registry  # noqa: E402
from libs.python.drivers.google.gmail import GmailDriver  # noqa: E402
from libs.python.drivers.llm import LLMTextGenerationDriver  # noqa: E402
from libs.python.graph import APINode, Graph, GraphExecutionResult, GraphExecutor  # noqa: E402
from libs.python.persistence import get_document_store  # noqa: E402
from libs.python.persistence.event_store import persist_event  # noqa: E402

# Default prompt documents (stored in DocumentStore on first use)
PER_EMAIL_PROMPT_DOC = {
    "name": "gmail_per_email_summary_v1",
    "kind": "email_summary",
    "description": "Per-email memo-style summary with urgency classification.",
    "text": (
        "You are an expert in e-communications. The user is looking for simple, "
        "legible summaries in the style of a short memo for each e-mail. "
        "Focus first on urgent communications such as medical appointments, bills, "
        "debts, government notices, or anything that cannot be ignored. "
        "Then cover messages from family and friends, and finally non-urgent "
        "administrative emails. For each email, extract key dates, obligations, "
        "and any personally identifying information that is important for action."
    ),
}

GLOBAL_SUMMARY_PROMPT_DOC = {
    "name": "gmail_global_summary_v1",
    "kind": "global_summary",
    "description": "Overall dashboard-style summary across all emails.",
    "text": (
        "You are an expert in e-communications. You will receive a list of emails "
        "with short memo-style summaries. Produce a high-level dashboard-style "
        "summary including: total number of emails, counts per urgency bucket "
        "(Critical, Family/Friends, Admin, Other), and a concise bullet list of "
        "the most critical actions and deadlines."
    ),
}


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


def _get_or_create_prompt_text(store, doc_def: dict) -> str:
    """Load prompt text from DocumentStore, creating a doc if missing.

    Prompts are stored in the shared "prompts" collection and keyed by name.
    """

    docs = store.query("prompts", {"name": doc_def["name"]}, limit=1)
    if docs:
        text_val = docs[0].data.get("text", "")
        return str(text_val) if text_val else str(doc_def["text"])

    store.create("prompts", doc_def)
    return str(doc_def["text"])


async def main() -> None:
    """Execute Gmail fetch workflow."""
    print("=" * 60)
    print("Gmail Fetch Example - Last 24 Hours")
    print("=" * 60)

    # Step 1: Register drivers
    print("\n[1] Registering drivers...")
    registry = get_global_registry()

    gmail_driver = GmailDriver()
    llm_driver = LLMTextGenerationDriver()
    registry.register("google.gmail", gmail_driver)
    registry.register("llm.text", llm_driver)

    print(f"    Registered: {registry.list_namespaces()}")

    # Step 2: Build graph with Gmail fetch and LLM summaries
    print("\n[2] Building graph...")
    graph = Graph()

    # Node: fetch unread emails from last 24 hours
    gmail_node = APINode(
        node_id="fetch_emails",
        driver_namespace="google.gmail",
        operation="list_unread",
        params={
            "limit": 25,
            "after_days": 1,
        },
    )
    graph.add_node(gmail_node)

    # Node: summarize emails via LLM driver
    summarize_node = APINode(
        node_id="summarize_emails",
        driver_namespace="llm.text",
        operation="generate_summary",
        params={},  # prompt will be provided via initial_inputs
    )
    graph.add_node(summarize_node)

    # Simple edge so executor orders nodes; prompt wiring is done via inputs
    graph.add_edge("fetch_emails", "summarize_emails")

    print(f"    Nodes: {list(graph.nodes.keys())}")
    print(f"    Edges: {graph.edges}")

    # Step 3: Prepare prompts and execute graph
    print("\n[3] Preparing prompts and executing graph...")

    # Execute first node to fetch emails, then build prompts
    executor = GraphExecutor()

    try:
        # First, run just the Gmail node to get emails
        partial_graph = Graph()
        partial_graph.add_node(gmail_node)
        gmail_result = await executor.execute(partial_graph)

        node_res = gmail_result.node_results.get("fetch_emails")
        emails = []
        if node_res and node_res.success:
            emails = node_res.output.get("data", {}).get("emails", []) or node_res.output.get("emails", [])

        # Persist event: Gmail fetch finished
        from contextlib import suppress

        with suppress(Exception):
            persist_event(
                service_id="gmail-graph",
                event_type="emails_fetched",
                payload={"count": len(emails)},
            )

        # Load or create prompt documents
        store = get_document_store()
        per_email_prompt = _get_or_create_prompt_text(store, PER_EMAIL_PROMPT_DOC)
        _get_or_create_prompt_text(store, GLOBAL_SUMMARY_PROMPT_DOC)  # Ensure doc exists

        # Simple text serialization of emails for now
        email_lines = []
        for idx, email in enumerate(emails, start=1):
            subject = email.get("subject", "(no subject)")
            sender = email.get("from", "(unknown)")
            date = email.get("date", "(unknown)")
            snippet = email.get("snippet", "")
            email_lines.append(f"[{idx}] Subject: {subject}\nFrom: {sender}\nDate: {date}\nSnippet: {snippet}\n")

        emails_block = "\n\n".join(email_lines) if email_lines else "(no emails)"

        combined_prompt = (
            per_email_prompt
            + "\n\nEMAILS:\n"  # marker
            + emails_block
            + "\n\nNow provide memo-style summaries and urgency classification for each email."
            + "\nThen provide an overall summary as described."
        )

        initial_inputs = {
            "summarize_emails": {
                "params": {
                    "prompt": combined_prompt,
                }
            }
        }

        # Execute full graph with prepared prompt
        full_result = await executor.execute(graph, initial_inputs=initial_inputs)

        # Persist events for graph execution
        with suppress(Exception):
            persist_event(
                service_id="gmail-graph",
                event_type="graph_executed",
                payload={
                    "graph_id": "e70a56db-5eba-43f8-a61f-ffd77f4febb7",
                    "emails_fetched": len(emails),
                    "success": full_result.success,
                    "execution_order": full_result.execution_order,
                },
            )

        _display_results(full_result)
    except Exception as exc:
        print(f"\n[!] Execution failed: {exc}")
        with suppress(Exception):
            persist_event(
                service_id="gmail-graph",
                event_type="graph_failed",
                payload={"error": str(exc)},
                level="ERROR",
            )
        import traceback

        traceback.print_exc()

    print("\n" + "=" * 60)
    print("Example complete")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
