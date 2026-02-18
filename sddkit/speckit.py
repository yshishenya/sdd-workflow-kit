from __future__ import annotations

import re
import subprocess
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class SpeckitUpstream:
    root: Path
    version_label: str


def ensure_speckit_upstream(kit_root: Path) -> SpeckitUpstream:
    """Return path to the vendored Spec Kit upstream, initializing submodules if needed.

    We vendor `github/spec-kit` as a git submodule under `upstreams/spec-kit`.
    In some environments (nested submodules, Actions), the submodule may not be
    initialized yet. We attempt to init it when the kit is a git checkout.
    """

    upstream = kit_root / "upstreams" / "spec-kit"
    marker = upstream / "templates" / "commands"
    if marker.is_dir():
        return SpeckitUpstream(root=upstream, version_label=_describe_git_head(upstream))

    # Attempt to init the submodule when running from a git checkout/submodule.
    git_dir = kit_root / ".git"
    if git_dir.exists():
        subprocess.run(
            ["git", "submodule", "update", "--init", "--recursive", "upstreams/spec-kit"],
            cwd=kit_root,
            check=True,
        )

    if not marker.is_dir():
        raise FileNotFoundError(
            "Spec Kit upstream is missing (expected `upstreams/spec-kit/templates/commands`). "
            "If this kit is used as a submodule, ensure submodules are checked out recursively."
        )

    return SpeckitUpstream(root=upstream, version_label=_describe_git_head(upstream))


def _describe_git_head(repo_root: Path) -> str:
    try:
        sha = (
            subprocess.run(
                ["git", "rev-parse", "HEAD"],
                cwd=repo_root,
                check=True,
                capture_output=True,
                text=True,
            )
            .stdout.strip()
        )
        tag = (
            subprocess.run(
                ["git", "describe", "--tags", "--exact-match"],
                cwd=repo_root,
                check=False,
                capture_output=True,
                text=True,
            )
            .stdout.strip()
        )
        if tag:
            return f"{tag} ({sha[:7]})"
        return sha[:12]
    except Exception:
        return "unknown"


def list_template_files(upstream: SpeckitUpstream) -> list[Path]:
    base = upstream.root / "templates"
    out: list[Path] = []
    for p in sorted(base.rglob("*")):
        if p.is_dir():
            continue
        rel = p.relative_to(base).as_posix()
        if rel.startswith("commands/"):
            continue
        if p.name == "vscode-settings.json":
            continue
        out.append(p)
    return out


def list_script_files(upstream: SpeckitUpstream, script_variant: str) -> list[Path]:
    if script_variant not in {"sh", "ps"}:
        raise ValueError(f"Unknown script_variant: {script_variant} (expected sh|ps)")
    subdir = "bash" if script_variant == "sh" else "powershell"
    base = upstream.root / "scripts" / subdir
    if not base.is_dir():
        raise FileNotFoundError(f"Spec Kit scripts dir not found: {base}")
    return [p for p in sorted(base.rglob("*")) if p.is_file()]


def list_command_templates(upstream: SpeckitUpstream) -> list[Path]:
    base = upstream.root / "templates" / "commands"
    return [p for p in sorted(base.glob("*.md")) if p.is_file()]


def rewrite_paths(text: str) -> str:
    # Mirrors Spec Kit's release packaging rewrite_paths() (bash) behavior.
    text = re.sub(r"(/?)memory/", ".specify/memory/", text)
    text = re.sub(r"(/?)scripts/", ".specify/scripts/", text)
    text = re.sub(r"(/?)templates/", ".specify/templates/", text)
    text = text.replace(".specify.specify/", ".specify/")
    return text


def generate_command_prompt(
    template_text: str,
    *,
    script_variant: str,
    agent: str,
    args_format: str,
) -> str:
    """Generate a markdown prompt from a Spec Kit command template.

    Reproduces the essential behavior of Spec Kit's release packaging script:
    - Extracts the script command for the chosen script variant (sh/ps) from YAML frontmatter.
    - Substitutes {SCRIPT}, {AGENT_SCRIPT} (if present), {ARGS}, and __AGENT__.
    - Removes frontmatter sections `scripts:` and `agent_scripts:` while preserving other YAML.
    - Rewrites memory/scripts/templates paths to `.specify/*`.
    """

    if script_variant not in {"sh", "ps"}:
        raise ValueError(f"Unknown script_variant: {script_variant} (expected sh|ps)")

    # Normalize line endings to match upstream packaging behavior.
    text = template_text.replace("\r", "")

    fm, body = _split_frontmatter(text)
    script_cmd = _extract_variant_value(fm, key="scripts", variant=script_variant) or f"(Missing script command for {script_variant})"
    agent_script_cmd = _extract_variant_value(fm, key="agent_scripts", variant=script_variant) or ""

    out = text
    out = out.replace("{SCRIPT}", script_cmd)
    if agent_script_cmd:
        out = out.replace("{AGENT_SCRIPT}", agent_script_cmd)
    out = out.replace("{ARGS}", args_format)
    out = out.replace("__AGENT__", agent)
    out = _strip_frontmatter_sections(out, sections={"scripts", "agent_scripts"})
    out = rewrite_paths(out)
    return out


def _split_frontmatter(text: str) -> tuple[list[str], str]:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return ([], text)
    # Find closing fence.
    end = None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            end = i
            break
    if end is None:
        return ([], text)
    fm = lines[1:end]
    rest = "\n".join(lines[end + 1 :])
    return (fm, rest)


def _extract_variant_value(frontmatter_lines: list[str], *, key: str, variant: str) -> str | None:
    in_section = False
    for line in frontmatter_lines:
        if not in_section:
            if line.strip() == f"{key}:":
                in_section = True
            continue
        # End section when a new top-level key starts.
        if line and not line[0].isspace():
            break
        m = re.match(rf"^\s*{re.escape(variant)}\s*:\s*(.*)$", line)
        if m:
            return m.group(1).strip()
    return None


def _strip_frontmatter_sections(text: str, *, sections: set[str]) -> str:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return text

    # Locate end of frontmatter.
    end = None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            end = i
            break
    if end is None:
        return text

    out_fm: list[str] = []
    skipping = False
    skip_keys = {f"{s}:" for s in sections}
    for line in lines[1:end]:
        if not skipping and line.strip() in skip_keys:
            skipping = True
            continue
        if skipping:
            # Skip indented continuation lines of the removed section.
            if line.startswith((" ", "\t")):
                continue
            skipping = False
            # Fall through to normal processing of the current line.
        out_fm.append(line)

    out_lines = ["---", *out_fm, "---", *lines[end + 1 :]]
    return "\n".join(out_lines) + ("\n" if text.endswith("\n") else "")

