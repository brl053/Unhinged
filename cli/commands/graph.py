#!/usr/bin/env python3
"""
@llm-type cli.command.graph
@llm-does CRUD operations for graph workflows via document store

Graph management CLI - Create, Read, Update, Delete graph workflows.
Graphs are stored in the document store under the "graphs" collection.
"""

import base64
from pathlib import Path
from typing import Any

import click

from cli.utils import log_error, log_info, log_success, log_warning


@click.group()
def graph():
    """Manage graph workflows (CRUD operations)."""
    pass


@graph.command(name="create")
@click.argument("file_path", type=click.Path(exists=True))
@click.option("--name", "-n", help="Graph name (defaults to filename)")
@click.option("--description", "-d", help="Graph description")
@click.option("--tags", "-t", multiple=True, help="Tags for categorization")
def create(file_path: str, name: str | None, description: str | None, tags: tuple[str, ...]):
    """Create a new graph from a file.

    The file can be:
    - JSON graph definition
    - Python graph script
    - Binary graph data

    Examples:
        unhinged graph create gmail_workflow.json
        unhinged graph create workflow.py --name "Email Processor"
        unhinged graph create graph.bin --tags email --tags automation
    """
    try:
        from libs.python.persistence import get_document_store

        path = Path(file_path)

        # Determine name
        graph_name = name or path.stem

        # Read file content
        if path.suffix in [".json", ".py", ".txt"]:
            # Text file - store as string
            content = path.read_text()
            content_type = "text"
            encoding = "utf-8"
        else:
            # Binary file - store as base64
            content = base64.b64encode(path.read_bytes()).decode("ascii")
            content_type = "binary"
            encoding = "base64"

        # Create document
        store = get_document_store()
        doc = store.create(
            "graphs",
            {
                "name": graph_name,
                "description": description or "",
                "file_name": path.name,
                "file_type": path.suffix,
                "content": content,
                "content_type": content_type,
                "encoding": encoding,
                "tags": list(tags),
            },
        )

        log_success(f"Graph created: {doc.id}")
        log_info(f"  Name: {graph_name}")
        log_info(f"  File: {path.name}")
        log_info(f"  Type: {content_type} ({encoding})")
        if tags:
            log_info(f"  Tags: {', '.join(tags)}")

        return 0

    except ImportError as e:
        log_error(f"Document store not available: {e}")
        log_warning("Install PostgreSQL dependencies: pip install psycopg2-binary")
        return 1
    except Exception as e:
        log_error(f"Failed to create graph: {e}")
        return 1


@graph.command(name="list")
@click.option("--tag", "-t", help="Filter by tag")
@click.option("--limit", "-l", default=100, help="Maximum results")
def list_graphs(tag: str | None, limit: int):
    """List all stored graphs.

    Examples:
        unhinged graph list
        unhinged graph list --tag email
        unhinged graph list --limit 10
    """
    try:
        from libs.python.persistence import get_document_store

        store = get_document_store()

        # Query graphs
        filters = {"tags": [tag]} if tag else None
        docs = store.query("graphs", filters=filters, limit=limit)

        if not docs:
            log_warning("No graphs found")
            return 0

        log_success(f"Found {len(docs)} graph(s):")
        print()

        for doc in docs:
            data = doc.data
            print(f"  ID: {doc.id}")
            print(f"  Name: {data.get('name', 'Unnamed')}")
            if data.get("description"):
                print(f"  Description: {data['description']}")
            print(f"  File: {data.get('file_name', 'N/A')}")
            print(f"  Type: {data.get('content_type', 'unknown')}")
            if data.get("tags"):
                print(f"  Tags: {', '.join(data['tags'])}")
            print(f"  Created: {doc.created_at}")
            print(f"  Updated: {doc.updated_at}")
            print()

        return 0

    except ImportError as e:
        log_error(f"Document store not available: {e}")
        return 1
    except Exception as e:
        log_error(f"Failed to list graphs: {e}")
        return 1


@graph.command(name="get")
@click.argument("graph_id")
@click.option("--output", "-o", type=click.Path(), help="Save to file")
def get(graph_id: str, output: str | None):
    """Get a graph by ID.

    Examples:
        unhinged graph get abc-123-def
        unhinged graph get abc-123-def --output workflow.json
    """
    try:
        from libs.python.persistence import get_document_store

        store = get_document_store()
        doc = store.read("graphs", graph_id)

        if not doc:
            log_error(f"Graph not found: {graph_id}")
            return 1

        data = doc.data

        # Display metadata
        log_success(f"Graph: {data.get('name', 'Unnamed')}")
        print()
        print(f"  ID: {doc.id}")
        print(f"  Name: {data.get('name', 'Unnamed')}")
        if data.get("description"):
            print(f"  Description: {data['description']}")
        print(f"  File: {data.get('file_name', 'N/A')}")
        print(f"  Type: {data.get('content_type', 'unknown')}")
        print(f"  Encoding: {data.get('encoding', 'unknown')}")
        if data.get("tags"):
            print(f"  Tags: {', '.join(data['tags'])}")
        print(f"  Created: {doc.created_at}")
        print(f"  Updated: {doc.updated_at}")
        print()

        # Decode content
        content = data.get("content", "")
        content_bytes = base64.b64decode(content) if data.get("encoding") == "base64" else content.encode("utf-8")

        # Output to file or stdout
        if output:
            output_path = Path(output)
            output_path.write_bytes(content_bytes)
            log_success(f"Saved to: {output}")
        else:
            # Print content (if text)
            if data.get("content_type") == "text":
                print("Content:")
                print("─" * 80)
                print(content)
                print("─" * 80)
            else:
                log_warning("Binary content - use --output to save to file")

        return 0

    except ImportError as e:
        log_error(f"Document store not available: {e}")
        return 1
    except Exception as e:
        log_error(f"Failed to get graph: {e}")
        return 1


@graph.command(name="update")
@click.argument("graph_id")
@click.option("--name", "-n", help="Update graph name")
@click.option("--description", "-d", help="Update description")
@click.option("--add-tag", "-t", multiple=True, help="Add tags")
@click.option("--file", "-f", type=click.Path(exists=True), help="Update content from file")
def update(graph_id: str, name: str | None, description: str | None, add_tag: tuple[str, ...], file: str | None):
    """Update a graph.

    Examples:
        unhinged graph update abc-123 --name "New Name"
        unhinged graph update abc-123 --description "Updated workflow"
        unhinged graph update abc-123 --add-tag production
        unhinged graph update abc-123 --file new_workflow.json
    """
    try:
        from libs.python.persistence import get_document_store

        store = get_document_store()
        doc = store.read("graphs", graph_id)

        if not doc:
            log_error(f"Graph not found: {graph_id}")
            return 1

        # Build update data
        updates: dict[str, Any] = {}

        if name:
            updates["name"] = name

        if description:
            updates["description"] = description

        if add_tag:
            existing_tags = doc.data.get("tags", [])
            updates["tags"] = list(set(existing_tags + list(add_tag)))

        if file:
            path = Path(file)
            if path.suffix in [".json", ".py", ".txt"]:
                content = path.read_text()
                updates["content"] = content
                updates["content_type"] = "text"
                updates["encoding"] = "utf-8"
            else:
                content = base64.b64encode(path.read_bytes()).decode("ascii")
                updates["content"] = content
                updates["content_type"] = "binary"
                updates["encoding"] = "base64"
            updates["file_name"] = path.name
            updates["file_type"] = path.suffix

        # Update document
        updated_doc = store.update("graphs", graph_id, updates)

        if updated_doc:
            log_success(f"Graph updated: {graph_id}")
            log_info(f"  Version: {updated_doc.version}")
            return 0
        else:
            log_error("Update failed")
            return 1

    except ImportError as e:
        log_error(f"Document store not available: {e}")
        return 1
    except Exception as e:
        log_error(f"Failed to update graph: {e}")
        return 1


@graph.command(name="delete")
@click.argument("graph_id")
@click.option("--yes", "-y", is_flag=True, help="Skip confirmation")
def delete(graph_id: str, yes: bool):
    """Delete a graph.

    Examples:
        unhinged graph delete abc-123
        unhinged graph delete abc-123 --yes
    """
    try:
        from libs.python.persistence import get_document_store

        store = get_document_store()
        doc = store.read("graphs", graph_id)

        if not doc:
            log_error(f"Graph not found: {graph_id}")
            return 1

        # Confirm deletion
        if not yes:
            graph_name = doc.data.get("name", "Unnamed")
            click.confirm(f"Delete graph '{graph_name}' ({graph_id})?", abort=True)

        # Delete
        if store.delete("graphs", graph_id):
            log_success(f"Graph deleted: {graph_id}")
            return 0
        else:
            log_error("Delete failed")
            return 1

    except ImportError as e:
        log_error(f"Document store not available: {e}")
        return 1
    except click.Abort:
        log_warning("Cancelled")
        return 1
    except Exception as e:
        log_error(f"Failed to delete graph: {e}")
        return 1


@graph.command(name="run")
@click.argument("graph_id")
def run(graph_id: str):
    """Execute a graph workflow.

    Examples:
        unhinged graph run abc-123
    """
    import sys
    import tempfile

    try:
        from libs.python.persistence import get_document_store

        store = get_document_store()
        doc = store.read("graphs", graph_id)

        if not doc:
            log_error(f"Graph not found: {graph_id}")
            return 1

        data = doc.data
        graph_name = data.get("name", "Unnamed")

        log_info(f"Running graph: {graph_name}")

        # Decode content
        content = data.get("content", "")
        content_bytes = base64.b64decode(content) if data.get("encoding") == "base64" else content.encode("utf-8")

        # Write to temp file and execute
        with tempfile.NamedTemporaryFile(mode="wb", suffix=".py", delete=False) as f:
            f.write(content_bytes)
            temp_path = f.name

        try:
            # Execute the Python file
            import subprocess

            result = subprocess.run([sys.executable, temp_path], capture_output=True, text=True)

            # Show output
            if result.stdout:
                print(result.stdout)
            if result.stderr:
                print(result.stderr, file=sys.stderr)

            if result.returncode == 0:
                log_success("Graph execution complete")
                return 0
            else:
                log_error(f"Graph execution failed (exit code: {result.returncode})")
                return 1

        finally:
            # Cleanup temp file
            import os

            os.unlink(temp_path)

    except ImportError as e:
        log_error(f"Document store not available: {e}")
        return 1
    except Exception as e:
        log_error(f"Failed to run graph: {e}")
        import traceback

        traceback.print_exc()
        return 1
