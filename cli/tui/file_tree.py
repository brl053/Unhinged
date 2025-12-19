"""File tree navigation component.

Renders directory structure as a navigable tree for the left pane.
Supports filtering, selection callbacks, and integration with widget corral.
"""

from pathlib import Path
from typing import Any

from rich.panel import Panel
from rich.tree import Tree

from cli.tui.console import console


def _get_icon(path: Path) -> str:
    """Get icon for file/directory based on type."""
    if path.is_dir():
        return "📁"

    suffix = path.suffix.lower()
    icons = {
        ".py": "🐍",
        ".json": "📋",
        ".yaml": "📋",
        ".yml": "📋",
        ".md": "📝",
        ".txt": "📄",
        ".sh": "⚙️",
        ".toml": "⚙️",
        ".cfg": "⚙️",
        ".log": "📜",
    }
    return icons.get(suffix, "📄")


def _should_include(path: Path, patterns: list[str] | None, exclude: list[str] | None) -> bool:
    """Check if path should be included based on patterns."""
    name = path.name

    # Skip hidden by default
    if name.startswith(".") and name not in (".env", ".gitignore"):
        return False

    # Skip common non-essential dirs
    skip_dirs = {"__pycache__", "node_modules", ".git", "venv", ".venv", "build", "dist"}
    if path.is_dir() and name in skip_dirs:
        return False

    # Apply exclude patterns
    if exclude:
        for pattern in exclude:
            if path.match(pattern):
                return False

    # Apply include patterns (if specified, only include matching)
    if patterns:
        return any(path.match(p) for p in patterns)

    return True


def _add_path_to_tree(
    tree: Tree,
    path: Path,
    depth: int,
    max_depth: int,
    patterns: list[str] | None,
    exclude: list[str] | None,
) -> None:
    """Recursively add path to tree."""
    if depth >= max_depth:
        return

    if not path.is_dir():
        return

    try:
        entries = sorted(path.iterdir(), key=lambda p: (not p.is_dir(), p.name.lower()))
    except PermissionError:
        return

    for entry in entries:
        if not _should_include(entry, patterns, exclude):
            continue

        icon = _get_icon(entry)
        label = f"{icon} {entry.name}"

        if entry.is_dir():
            branch = tree.add(f"[bold]{label}[/bold]")
            _add_path_to_tree(branch, entry, depth + 1, max_depth, patterns, exclude)
        else:
            style = "dim" if entry.suffix in {".pyc", ".log"} else ""
            tree.add(f"[{style}]{label}[/{style}]" if style else label)


def file_tree(
    root: str | Path = ".",
    *,
    max_depth: int = 3,
    patterns: list[str] | None = None,
    exclude: list[str] | None = None,
    title: str | None = None,
) -> None:
    """Render a file tree to console.

    Args:
        root: Root directory path.
        max_depth: Maximum depth to traverse.
        patterns: Include only files matching these glob patterns.
        exclude: Exclude files matching these glob patterns.
        title: Custom title for tree root.
    """
    root_path = Path(root).resolve()

    if not root_path.exists():
        console.print(f"[error]Path not found: {root}[/error]")
        return

    display_name = title or root_path.name or str(root_path)
    tree = Tree(f"[bold cyan]📂 {display_name}[/bold cyan]")

    _add_path_to_tree(tree, root_path, 0, max_depth, patterns, exclude)

    console.print()
    console.print(tree)
    console.print()


def file_tree_panel(
    root: str | Path = ".",
    *,
    max_depth: int = 3,
    patterns: list[str] | None = None,
    exclude: list[str] | None = None,
    title: str | None = None,
    width: int | None = None,
) -> Panel:
    """Return file tree as a Panel widget (for layout composition).

    Args:
        root: Root directory path.
        max_depth: Maximum depth to traverse.
        patterns: Include only files matching these glob patterns.
        exclude: Exclude files matching these glob patterns.
        title: Panel title.
        width: Panel width.

    Returns:
        Rich Panel containing the file tree.
    """
    root_path = Path(root).resolve()

    if not root_path.exists():
        return Panel("[error]Path not found[/error]", title="Files", border_style="red")

    display_name = root_path.name or str(root_path)
    tree = Tree(f"[bold]{display_name}[/bold]")

    _add_path_to_tree(tree, root_path, 0, max_depth, patterns, exclude)

    return Panel(
        tree,
        title=title or "[ Files ]",
        border_style="cyan",
        width=width,
    )


def file_tree_data(
    root: str | Path = ".",
    *,
    max_depth: int = 3,
    patterns: list[str] | None = None,
    exclude: list[str] | None = None,
) -> dict[str, Any]:
    """Return file tree as structured data for programmatic use.

    Returns dict with:
        - name: directory name
        - path: absolute path string
        - children: list of child dicts (recursive)
        - is_dir: boolean
    """
    root_path = Path(root).resolve()

    def build_node(path: Path, depth: int) -> dict[str, Any] | None:
        if not _should_include(path, patterns, exclude):
            return None

        node: dict[str, Any] = {
            "name": path.name,
            "path": str(path),
            "is_dir": path.is_dir(),
        }

        if path.is_dir() and depth < max_depth:
            children = []
            try:
                for entry in sorted(path.iterdir(), key=lambda p: (not p.is_dir(), p.name.lower())):
                    child = build_node(entry, depth + 1)
                    if child:
                        children.append(child)
            except PermissionError:
                pass
            node["children"] = children

        return node

    result = build_node(root_path, 0)
    return result or {"name": str(root_path), "path": str(root_path), "is_dir": True, "children": []}
