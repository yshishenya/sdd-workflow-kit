from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from . import __version__


MANAGED_MARKER = "managed-by: sdd-workflow-kit"


@dataclass(frozen=True)
class ManagedFile:
    relpath: str
    kind: str  # markdown|yaml|text
    template: str


def is_managed_file(path: Path) -> bool:
    if not path.exists() or not path.is_file():
        return False
    try:
        head = path.read_text(encoding="utf-8", errors="replace").splitlines()[:15]
    except Exception:
        return False
    return any(MANAGED_MARKER in line for line in head)


def managed_header(kind: str, template: str) -> str:
    if kind == "markdown":
        return (
            "<!--\n"
            f"{MANAGED_MARKER}\n"
            f"kit-version: {__version__}\n"
            f"template: {template}\n"
            "-->\n\n"
        )
    if kind == "yaml":
        return (
            f"# {MANAGED_MARKER}\n"
            f"# kit-version: {__version__}\n"
            f"# template: {template}\n\n"
        )
    return f"{MANAGED_MARKER} kit-version={__version__} template={template}\n\n"

