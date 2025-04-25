import os
import shutil
import tempfile
from typing import List, Set, Optional

template_path = os.path.join(os.path.dirname(__file__), "template")


def clone_template():
    temp_path = os.path.join(tempfile.mkdtemp(), "vibe_coding")
    shutil.copytree(template_path, temp_path)
    shutil.rmtree(os.path.join(temp_path, "node_modules"), ignore_errors=True)
    return temp_path


def generate_directory_tree(path: str, ignore_dirs: Optional[Set[str]] = None) -> str:
    """
    Generate a visual representation of the directory structure.

    Args:
        path: The path to the directory to visualize
        ignore_dirs: Set of directory names to ignore (defaults to {"node_modules"})

    Returns:
        A formatted string representing the directory tree
    """
    if ignore_dirs is None:
        ignore_dirs = {"node_modules", ".git", ".venv"}

    # Normalize the path
    root_path = os.path.abspath(os.path.expanduser(path))
    root_name = os.path.basename(root_path) or root_path

    # Start the tree with the root
    tree_str = ".\n"

    # Get all directories and files
    items = _get_directory_contents(root_path, ignore_dirs)

    # Generate the tree representation
    tree_str += _format_tree(items, "", root_path)

    return tree_str


def _get_directory_contents(path: str, ignore_dirs: Set[str]) -> List[str]:
    """
    Get all files and directories in a path, sorted with directories first

    Args:
        path: The directory path to scan
        ignore_dirs: Set of directory names to ignore

    Returns:
        List of paths relative to the provided path
    """
    items = []

    try:
        # List all files and directories
        all_items = os.listdir(path)

        # Sort items (directories first)
        dirs = []
        files = []

        for item in sorted(all_items):
            full_path = os.path.join(path, item)
            if os.path.isdir(full_path):
                if item not in ignore_dirs:
                    dirs.append(item)
            else:
                files.append(item)

        items = dirs + files
    except (PermissionError, FileNotFoundError):
        pass

    return items


def _format_tree(
    items: List[str], prefix: str, path: str, ignore_dirs: Optional[Set[str]] = None
) -> str:
    """
    Format the directory contents as a tree structure with proper indentation

    Args:
        items: List of filenames or directory names
        prefix: Current line prefix for indentation
        path: Current directory path
        ignore_dirs: Set of directory names to ignore

    Returns:
        Formatted tree string for the current level
    """
    if ignore_dirs is None:
        ignore_dirs = {"node_modules"}

    tree_str = ""
    count = len(items)

    for i, item in enumerate(items):
        # Determine if this is the last item at this level
        is_last = i == count - 1

        # Choose the appropriate connector symbols
        conn = "└── " if is_last else "├── "
        next_prefix = "    " if is_last else "│   "

        # Add the current item to the tree
        tree_str += f"{prefix}{conn}{item}\n"

        # Recursively process subdirectories
        item_path = os.path.join(path, item)
        if os.path.isdir(item_path) and item not in ignore_dirs:
            sub_items = _get_directory_contents(item_path, ignore_dirs)
            if sub_items:
                tree_str += _format_tree(
                    sub_items, prefix + next_prefix, item_path, ignore_dirs
                )

    return tree_str
