from __future__ import annotations

from dataclasses import dataclass
from importlib import resources
import re
from typing import Iterable


@dataclass(frozen=True)
class TemplateData:
    text: str


def load_template(locale: str, name: str) -> TemplateData:
    # name examples:
    # - agents/AGENTS.md.tmpl
    # - github/workflows/sdd-kit-check.yml.tmpl
    # - docs/templates/ADR-Template.md.tmpl
    path = f"_templates/{locale}/{name}"
    try:
        txt = resources.files("sddkit").joinpath(path).read_text(encoding="utf-8")
    except FileNotFoundError:
        # Fallback to en
        txt = resources.files("sddkit").joinpath(f"_templates/en/{name}").read_text(encoding="utf-8")
    return TemplateData(text=txt)


def list_template_names(locale: str, root: str) -> list[str]:
    """List template file names (ending with .tmpl) under a template root.

    Returns names relative to the locale root, suitable for `load_template(locale, name)`.

    Example:
    - root="scaffolds/memory_bank"
    - returns ["scaffolds/memory_bank/README.md.tmpl", ...]
    """

    def walk(node: object, prefix: str) -> Iterable[str]:
        # `node` is an importlib.resources Traversable-like.
        for child in node.iterdir():  # type: ignore[attr-defined]
            child_name = getattr(child, "name", None) or str(child)
            child_prefix = f"{prefix}/{child_name}" if prefix else child_name
            if child.is_dir():  # type: ignore[attr-defined]
                yield from walk(child, child_prefix)
                continue
            if child_prefix.endswith(".tmpl"):
                yield child_prefix

    base = resources.files("sddkit").joinpath(f"_templates/{locale}/{root}")
    if not base.exists():
        base = resources.files("sddkit").joinpath(f"_templates/en/{root}")
        locale = "en"
    names = sorted(set(walk(base, root)))
    return names


def render_template(template_text: str, data: dict[str, str]) -> str:
    # Use a placeholder syntax that does not conflict with Markdown, shell, or currency.
    # Supported: {{var}} where var matches [A-Za-z_][A-Za-z0-9_]*
    pattern = re.compile(r"\{\{\s*([A-Za-z_][A-Za-z0-9_]*)\s*\}\}")

    def repl(match: re.Match[str]) -> str:
        key = match.group(1)
        return data.get(key, match.group(0))

    return pattern.sub(repl, template_text)
