#!/usr/bin/env python3
"""
Automated import updater for v0.3.1 project restructure.

Updates all internal imports from flat structure to feature-based structure.
"""

import re
from pathlib import Path
from typing import Dict, List, Tuple

# Import mapping: old_import → new_import
IMPORT_MAPPINGS: Dict[str, str] = {
    # Core
    "from uvisbox_assistant.graph import": "from uvisbox_assistant.core.graph import",
    "from uvisbox_assistant.nodes import": "from uvisbox_assistant.core.nodes import",
    "from uvisbox_assistant.routing import": "from uvisbox_assistant.core.routing import",
    "from uvisbox_assistant.state import": "from uvisbox_assistant.core.state import",
    "import uvisbox_assistant.graph": "import uvisbox_assistant.core.graph",
    "import uvisbox_assistant.nodes": "import uvisbox_assistant.core.nodes",
    "import uvisbox_assistant.routing": "import uvisbox_assistant.core.routing",
    "import uvisbox_assistant.state": "import uvisbox_assistant.core.state",

    # Tools
    "from uvisbox_assistant.data_tools import": "from uvisbox_assistant.tools.data_tools import",
    "from uvisbox_assistant.vis_tools import": "from uvisbox_assistant.tools.vis_tools import",
    "from uvisbox_assistant.statistics_tools import": "from uvisbox_assistant.tools.statistics_tools import",
    "from uvisbox_assistant.analyzer_tools import": "from uvisbox_assistant.tools.analyzer_tools import",
    "import uvisbox_assistant.data_tools": "import uvisbox_assistant.tools.data_tools",
    "import uvisbox_assistant.vis_tools": "import uvisbox_assistant.tools.vis_tools",
    "import uvisbox_assistant.statistics_tools": "import uvisbox_assistant.tools.statistics_tools",
    "import uvisbox_assistant.analyzer_tools": "import uvisbox_assistant.tools.analyzer_tools",

    # Session
    "from uvisbox_assistant.conversation import": "from uvisbox_assistant.session.conversation import",
    "from uvisbox_assistant.hybrid_control import": "from uvisbox_assistant.session.hybrid_control import",
    "from uvisbox_assistant.command_parser import": "from uvisbox_assistant.session.command_parser import",
    "import uvisbox_assistant.conversation": "import uvisbox_assistant.session.conversation",
    "import uvisbox_assistant.hybrid_control": "import uvisbox_assistant.session.hybrid_control",
    "import uvisbox_assistant.command_parser": "import uvisbox_assistant.session.command_parser",

    # LLM
    "from uvisbox_assistant.model import": "from uvisbox_assistant.llm.model import",
    "import uvisbox_assistant.model": "import uvisbox_assistant.llm.model",

    # Errors
    "from uvisbox_assistant.error_tracking import": "from uvisbox_assistant.errors.error_tracking import",
    "from uvisbox_assistant.error_interpretation import": "from uvisbox_assistant.errors.error_interpretation import",
    "import uvisbox_assistant.error_tracking": "import uvisbox_assistant.errors.error_tracking",
    "import uvisbox_assistant.error_interpretation": "import uvisbox_assistant.errors.error_interpretation",

    # Utils
    "from uvisbox_assistant.logger import": "from uvisbox_assistant.utils.logger import",
    "from uvisbox_assistant.output_control import": "from uvisbox_assistant.utils.output_control import",
    "from uvisbox_assistant.utils import": "from uvisbox_assistant.utils.utils import",
    "import uvisbox_assistant.logger": "import uvisbox_assistant.utils.logger",
    "import uvisbox_assistant.output_control": "import uvisbox_assistant.utils.output_control",
}

def update_file_imports(file_path: Path, dry_run: bool = False) -> Tuple[int, List[str]]:
    """
    Update imports in a single file.

    Returns:
        (number_of_changes, list_of_changes)
    """
    with open(file_path, 'r') as f:
        content = f.read()

    original_content = content
    changes = []

    for old_import, new_import in IMPORT_MAPPINGS.items():
        if old_import in content:
            content = content.replace(old_import, new_import)
            changes.append(f"{old_import} → {new_import}")

    num_changes = len(changes)

    if num_changes > 0 and not dry_run:
        with open(file_path, 'w') as f:
            f.write(content)

    return num_changes, changes

def main():
    """Update all imports in the codebase."""
    import argparse

    parser = argparse.ArgumentParser(description="Update imports for v0.3.1 restructure")
    parser.add_argument("--dry-run", action="store_true", help="Show changes without modifying files")
    args = parser.parse_args()

    # Files to update
    src_dir = Path("src/uvisbox_assistant")
    test_dir = Path("tests")

    # Find all Python files
    py_files = list(src_dir.rglob("*.py")) + list(test_dir.rglob("*.py"))
    py_files.append(Path("main.py"))  # Root main.py

    total_files_changed = 0
    total_changes = 0

    print(f"{'DRY RUN - ' if args.dry_run else ''}Updating imports in {len(py_files)} files...")
    print()

    for py_file in py_files:
        num_changes, changes = update_file_imports(py_file, dry_run=args.dry_run)

        if num_changes > 0:
            total_files_changed += 1
            total_changes += num_changes
            print(f"✓ {py_file} ({num_changes} changes)")
            for change in changes:
                print(f"  - {change}")
            print()

    print(f"{'Would update' if args.dry_run else 'Updated'} {total_changes} imports in {total_files_changed} files")

    if args.dry_run:
        print("\nRun without --dry-run to apply changes")

if __name__ == "__main__":
    main()
