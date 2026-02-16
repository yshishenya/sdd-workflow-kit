from __future__ import annotations

import os
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from . import __version__
from .config import SddKitConfig
from .managed import MANAGED_MARKER, ManagedFile, is_managed_file, managed_header
from .skills import list_skillpack_skills
from .templates import list_template_names, load_template, render_template


@dataclass(frozen=True)
class PlannedWrite:
    target: Path
    content: str
    reason: str
    mode: int | None = None


@dataclass(frozen=True)
class PlannedSkip:
    target: Path
    reason: str


@dataclass(frozen=True)
class PlannedUnmanaged:
    target: Path
    reason: str


@dataclass(frozen=True)
class PlannedCopyDir:
    source: Path
    target: Path
    reason: str


PlanItem = PlannedWrite | PlannedSkip | PlannedUnmanaged | PlannedCopyDir


def _kit_root() -> Path:
    # When running from a checkout, this points to repo root.
    return Path(__file__).resolve().parents[1]


def _project_rel(p: Path, root: Path) -> str:
    try:
        return str(p.relative_to(root))
    except Exception:
        return str(p)


def _infer_commands(detection: dict[str, str]) -> dict[str, str]:
    langs = set((detection.get("languages") or "").split(","))
    pms = set((detection.get("package_managers") or "").split(","))

    install_cmd = ""
    test_cmd = ""
    lint_cmd = ""
    format_cmd = ""

    if "python" in langs:
        if "uv" in pms:
            install_cmd = "uv sync"
            test_cmd = "uv run pytest"
            lint_cmd = "uv run ruff check ."
            format_cmd = "uv run ruff format ."
        else:
            install_cmd = "python -m pip install -e ."
            test_cmd = "pytest"
            lint_cmd = "python -m ruff check ."
            format_cmd = "python -m ruff format ."

    if "node" in langs:
        if "pnpm" in pms:
            install_cmd = install_cmd or "pnpm install"
            test_cmd = test_cmd or "pnpm test"
            lint_cmd = lint_cmd or "pnpm lint"
            format_cmd = format_cmd or "pnpm format"
        elif "yarn" in pms:
            install_cmd = install_cmd or "yarn install"
            test_cmd = test_cmd or "yarn test"
            lint_cmd = lint_cmd or "yarn lint"
            format_cmd = format_cmd or "yarn format"
        elif "bun" in pms:
            install_cmd = install_cmd or "bun install"
            test_cmd = test_cmd or "bun test"
            lint_cmd = lint_cmd or "bun run lint"
            format_cmd = format_cmd or "bun run format"
        else:
            install_cmd = install_cmd or "npm ci"
            test_cmd = test_cmd or "npm test"
            lint_cmd = lint_cmd or "npm run lint"
            format_cmd = format_cmd or "npm run format"

    return {
        "install_cmd": install_cmd or "(define in .sddkit/config.toml)",
        "test_cmd": test_cmd or "(define in .sddkit/config.toml)",
        "lint_cmd": lint_cmd or "(define in .sddkit/config.toml)",
        "format_cmd": format_cmd or "(define in .sddkit/config.toml)",
    }


def _render_agents_md(*, project_root: Path, kit_root: Path, cfg: SddKitConfig, detection: dict[str, str], locale: str) -> str:
    agents_tmpl = "agents/AGENTS.airis.md.tmpl" if (cfg.profile == "airis" or cfg.manage_memory_bank) else "agents/AGENTS.md.tmpl"
    tpl = load_template(locale, agents_tmpl).text

    skillpack_dir = kit_root / "skillpacks" / cfg.skills_default_pack
    skills = list_skillpack_skills(skillpack_dir)
    skills_lines = []
    for s in skills:
        # Keep it one line per skill to reduce churn.
        skills_lines.append(f"- {s.name}: {s.description} (file: {s.rel_path})")
    skills_block = "\n".join(skills_lines) if skills_lines else "- (no skillpack found; run `sdd-kit import-codex-skills` in the kit repo)"

    cmds = _infer_commands(detection)
    data = {
        "kit_version": __version__,
        "project_name": cfg.project_name,
        "integration_branch": cfg.integration_branch,
        "is_fork": "true" if cfg.is_fork else "false",
        "upstream_project": cfg.upstream_project,
        "memory_bank_root": cfg.memory_bank_root,
        "meta_sdd_root": cfg.meta_sdd_root,
        "meta_tools_root": cfg.meta_tools_root,
        "languages": detection.get("languages", ""),
        "package_managers": detection.get("package_managers", ""),
        "install_cmd": cmds["install_cmd"],
        "test_cmd": cmds["test_cmd"],
        "lint_cmd": cmds["lint_cmd"],
        "format_cmd": cmds["format_cmd"],
        "skills_block": skills_block,
        "codex_home": os.environ.get("CODEX_HOME", str(Path.home() / ".codex")),
        "kit_path": cfg.github_kit_path,
    }
    rendered = render_template(tpl, data)

    frag = project_root / ".sddkit" / "fragments" / "AGENTS.append.md"
    if frag.exists():
        rendered += "\n\n---\n\n" + frag.read_text(encoding="utf-8", errors="replace").rstrip() + "\n"

    return rendered


def _render_docs_template(locale: str, name: str, data: dict[str, str]) -> str:
    tpl = load_template(locale, f"docs/templates/{name}.tmpl").text
    return render_template(tpl, data)


def _render_workflow(locale: str, cfg: SddKitConfig, detection: dict[str, str]) -> str:
    tpl = load_template(locale, "github/workflows/sdd-kit-check.yml.tmpl").text
    return render_template(
        tpl,
        {
            "has_github_actions": detection.get("has_github_actions", "false"),
            "kit_path": cfg.github_kit_path,
            "config_path": cfg.github_config_path,
            "fail_on_missing_config": "true" if cfg.github_fail_on_missing_config else "false",
        },
    )


def _template_kind_for_path(path: Path) -> str:
    ext = path.suffix.lower()
    if ext == ".md":
        return "markdown"
    if ext in {".yml", ".yaml"}:
        return "yaml"
    # For file types where a header could break parsing or executability, keep templates "raw".
    if ext in {".sh", ".py", ".toml", ".json", ".dockerfile"}:
        return "raw"
    return "text"


def _plan_from_template_tree(
    *,
    project_root: Path,
    kit_root: Path,
    cfg: SddKitConfig,
    detection: dict[str, str],
    locale: str,
    template_root: str,
    dest_root: str,
    extra_data: dict[str, str],
    exec_mode: int | None = None,
) -> list[PlanItem]:
    # template_root is relative to templates locale root, e.g. "scaffolds/memory_bank"
    # dest_root is relative to project root, e.g. "meta/memory_bank"
    dest_root = dest_root.strip("/").rstrip("/")
    names = list_template_names(locale, template_root)

    cmds = _infer_commands(detection)
    data = {
        "kit_version": __version__,
        "project_name": cfg.project_name,
        "integration_branch": cfg.integration_branch,
        "upstream_project": cfg.upstream_project,
        "memory_bank_root": cfg.memory_bank_root,
        "meta_sdd_root": cfg.meta_sdd_root,
        "meta_tools_root": cfg.meta_tools_root,
        "docs_root": cfg.docs_root,
        "specs_root": cfg.specs_root,
        "languages": detection.get("languages", ""),
        "package_managers": detection.get("package_managers", ""),
        "install_cmd": cmds["install_cmd"],
        "test_cmd": cmds["test_cmd"],
        "lint_cmd": cmds["lint_cmd"],
        "format_cmd": cmds["format_cmd"],
        **extra_data,
    }

    plan: list[PlanItem] = []
    for name in names:
        if not name.endswith(".tmpl"):
            continue
        rel_inside = name.removeprefix(template_root).lstrip("/")
        out_rel = rel_inside.removesuffix(".tmpl")
        target = project_root / dest_root / out_rel

        tmpl = load_template(locale, name).text
        body = render_template(tmpl, data)

        # Executable scaffolds (meta/tools) must keep shebang first.
        kind = "raw" if exec_mode is not None else _template_kind_for_path(target)
        if kind == "raw":
            content = body
        else:
            content = managed_header(kind, name) + body

        if target.exists() and cfg.safe_mode and not is_managed_file(target):
            plan.append(PlannedUnmanaged(target=target, reason="exists but is not managed (safe_mode)"))
            continue

        reason = "create" if not target.exists() else ("update (managed)" if is_managed_file(target) else "update")
        mode = exec_mode if exec_mode is not None else None
        plan.append(PlannedWrite(target=target, content=content, reason=reason, mode=mode))

    return plan


def _plan_writes(project_root: Path, kit_root: Path, cfg: SddKitConfig, detection: dict[str, str], locale: str) -> list[PlanItem]:
    plan: list[PlanItem] = []

    docs_root = cfg.docs_root.strip("/").rstrip("/") or "docs"
    specs_root = cfg.specs_root.strip("/").rstrip("/") or "specs"

    managed: list[ManagedFile] = []
    if cfg.manage_agents_md:
        agents_tmpl = "agents/AGENTS.airis.md.tmpl" if (cfg.profile == "airis" or cfg.manage_memory_bank) else "agents/AGENTS.md.tmpl"
        managed.append(ManagedFile(relpath="AGENTS.md", kind="markdown", template=agents_tmpl))
    if cfg.manage_github_workflow and detection.get("has_github_actions") == "true":
        managed.append(ManagedFile(relpath=".github/workflows/sdd-kit-check.yml", kind="yaml", template="github/workflows/sdd-kit-check.yml.tmpl"))

    if cfg.manage_docs_scaffold:
        managed.extend(
            [
                ManagedFile(relpath=f"{docs_root}/templates/ADR-Template.md", kind="markdown", template="docs/templates/ADR-Template.md.tmpl"),
                ManagedFile(relpath=f"{docs_root}/templates/Feature-Template.md", kind="markdown", template="docs/templates/Feature-Template.md.tmpl"),
                ManagedFile(relpath=f"{docs_root}/templates/Architecture-Template.md", kind="markdown", template="docs/templates/Architecture-Template.md.tmpl"),
                ManagedFile(relpath=f"{docs_root}/Architecture/Overview.md", kind="markdown", template="docs/templates/Architecture__Overview.md.tmpl"),
                ManagedFile(relpath=f"{docs_root}/SDD/README.md", kind="markdown", template="docs/templates/SDD__README.md.tmpl"),
                ManagedFile(relpath=f"{docs_root}/ADR/.keep", kind="text", template="docs/.keep.tmpl"),
                ManagedFile(relpath=f"{docs_root}/Features/.keep", kind="text", template="docs/.keep.tmpl"),
            ]
        )

    if cfg.manage_specs_scaffold:
        # Directories are created as needed by writing README placeholders (keeps plan explicit).
        managed.extend(
            [
                ManagedFile(relpath=f"{specs_root}/README.md", kind="markdown", template="specs/README.md.tmpl"),
                ManagedFile(relpath=f"{specs_root}/active/.keep", kind="text", template="specs/.keep.tmpl"),
                ManagedFile(relpath=f"{specs_root}/pending/.keep", kind="text", template="specs/.keep.tmpl"),
                ManagedFile(relpath=f"{specs_root}/completed/.keep", kind="text", template="specs/.keep.tmpl"),
            ]
        )

    base_data = {"kit_version": __version__}

    for mf in managed:
        target = project_root / mf.relpath
        if mf.relpath == "AGENTS.md":
            body = _render_agents_md(project_root=project_root, kit_root=kit_root, cfg=cfg, detection=detection, locale=locale)
        elif mf.relpath.endswith("sdd-kit-check.yml"):
            body = _render_workflow(locale, cfg, detection)
        elif mf.relpath.startswith(f"{docs_root}/"):
            # Map to template file name.
            tmpl_name = mf.relpath.replace("/", "__")
            # We keep a small map for clarity.
            if mf.relpath == f"{docs_root}/templates/ADR-Template.md":
                body = _render_docs_template(locale, "ADR-Template.md", base_data)
            elif mf.relpath == f"{docs_root}/templates/Feature-Template.md":
                body = _render_docs_template(locale, "Feature-Template.md", base_data)
            elif mf.relpath == f"{docs_root}/templates/Architecture-Template.md":
                body = _render_docs_template(locale, "Architecture-Template.md", base_data)
            elif mf.relpath == f"{docs_root}/Architecture/Overview.md":
                body = _render_docs_template(locale, "Architecture__Overview.md", base_data)
            elif mf.relpath == f"{docs_root}/SDD/README.md":
                body = _render_docs_template(locale, "SDD__README.md", base_data)
            else:
                body = f"# Placeholder ({tmpl_name})\n"
        elif mf.relpath.startswith(f"{specs_root}/") and mf.relpath.endswith(".keep"):
            body = ""
        elif mf.relpath == f"{specs_root}/README.md":
            tpl = load_template(locale, "specs/README.md.tmpl").text
            body = render_template(tpl, base_data)
        else:
            body = ""

        content = managed_header("markdown" if mf.kind == "markdown" else ("yaml" if mf.kind == "yaml" else "text"), mf.template) + body

        if target.exists() and cfg.safe_mode and not is_managed_file(target):
            plan.append(PlannedUnmanaged(target=target, reason="exists but is not managed (safe_mode)"))
            continue

        reason = "create" if not target.exists() else ("update (managed)" if is_managed_file(target) else "update")
        plan.append(PlannedWrite(target=target, content=content, reason=reason))

    # Profile-driven scaffolds (Memory Bank + meta tools + meta/sdd).
    if cfg.manage_memory_bank:
        plan += _plan_from_template_tree(
            project_root=project_root,
            kit_root=kit_root,
            cfg=cfg,
            detection=detection,
            locale=locale,
            template_root="scaffolds/memory_bank",
            dest_root=cfg.memory_bank_root,
            extra_data={},
        )

    if cfg.manage_meta_tools:
        plan += _plan_from_template_tree(
            project_root=project_root,
            kit_root=kit_root,
            cfg=cfg,
            detection=detection,
            locale=locale,
            template_root="scaffolds/meta_tools",
            dest_root=cfg.meta_tools_root,
            extra_data={},
            exec_mode=0o755,
        )

    if cfg.manage_meta_sdd:
        plan += _plan_from_template_tree(
            project_root=project_root,
            kit_root=kit_root,
            cfg=cfg,
            detection=detection,
            locale=locale,
            template_root="scaffolds/meta_sdd",
            dest_root=cfg.meta_sdd_root,
            extra_data={},
        )

    if cfg.manage_codex_scaffold:
        plan += _plan_from_template_tree(
            project_root=project_root,
            kit_root=kit_root,
            cfg=cfg,
            detection=detection,
            locale=locale,
            template_root="scaffolds/codex",
            dest_root=cfg.codex_root,
            extra_data={},
        )

    return plan


def sync_project(
    project_root: Path,
    *,
    config_path: Path,
    cfg: SddKitConfig,
    detection: dict[str, str],
    locale: str,
    dry_run: bool,
    skills_install_pack: str | None = None,
    skills_install_to: str | None = None,
    skills_install_only: bool = False,
) -> None:
    kit_root = _kit_root()
    plan: list[PlanItem] = []
    if not skills_install_only:
        plan += _plan_writes(project_root, kit_root, cfg, detection, locale)

    if skills_install_pack is not None:
        plan += _plan_skill_install(project_root, kit_root, pack=skills_install_pack, dest=skills_install_to or cfg.skills_default_install_to)

    for item in plan:
        if isinstance(item, PlannedSkip):
            print(f"SKIP {_project_rel(item.target, project_root)} ({item.reason})")
            continue
        if isinstance(item, PlannedUnmanaged):
            print(f"SKIP {_project_rel(item.target, project_root)} ({item.reason})")
            continue
        if isinstance(item, PlannedCopyDir):
            print(f"COPY {_project_rel(item.target, project_root)} ({item.reason})")
            if dry_run:
                continue
            item.target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copytree(item.source, item.target, dirs_exist_ok=False)
            continue
        print(f"WRITE {_project_rel(item.target, project_root)} ({item.reason})")
        if dry_run:
            continue
        item.target.parent.mkdir(parents=True, exist_ok=True)
        item.target.write_text(item.content, encoding="utf-8")
        if item.mode is not None:
            os.chmod(item.target, item.mode)

    if skills_install_only:
        return

    if not dry_run:
        _ensure_config_notice(project_root, config_path)


def _ensure_config_notice(project_root: Path, config_path: Path) -> None:
    # Small helper file to make it obvious where to add local overrides.
    p = project_root / ".sddkit" / "fragments" / ".gitkeep"
    p.parent.mkdir(parents=True, exist_ok=True)
    if not p.exists():
        p.write_text("", encoding="utf-8")


def check_project(project_root: Path, *, config_path: Path, cfg: SddKitConfig, detection: dict[str, str], locale: str) -> bool:
    kit_root = _kit_root()
    plan = _plan_writes(project_root, kit_root, cfg, detection, locale)

    ok = True
    for item in plan:
        if isinstance(item, PlannedUnmanaged):
            print(f"UNMANAGED {_project_rel(item.target, project_root)}")
            ok = False
            continue
        if isinstance(item, PlannedSkip):
            # Skipped files are outside of management scope.
            continue
        if not item.target.exists():
            print(f"MISSING {_project_rel(item.target, project_root)}")
            ok = False
            continue
        actual = item.target.read_text(encoding="utf-8", errors="replace")
        if actual != item.content:
            print(f"DRIFT {_project_rel(item.target, project_root)}")
            ok = False

    return ok


def _plan_skill_install(project_root: Path, kit_root: Path, *, pack: str, dest: str) -> list[PlanItem]:
    pack_root = kit_root / "skillpacks" / pack / "skills"
    if not pack_root.exists():
        return [PlannedSkip(target=pack_root, reason=f"skillpack not found: {pack}")]

    if dest == "project":
        dest_root = project_root / ".codex" / "skills"
    elif dest == "global":
        codex_home = Path(os.environ.get("CODEX_HOME", str(Path.home() / ".codex")))
        dest_root = codex_home / "skills"
    else:
        return [PlannedSkip(target=pack_root, reason=f"unknown skills destination: {dest}")]

    items: list[PlanItem] = []
    skill_dirs = sorted({p.parent for p in pack_root.rglob("SKILL.md")})
    for skill_dir in skill_dirs:
        if not skill_dir.is_dir():
            continue
        rel = skill_dir.relative_to(pack_root)
        dst = dest_root / rel
        if dst.exists():
            items.append(PlannedSkip(target=dst, reason="skill dir already exists"))
            continue
        items.append(PlannedCopyDir(source=skill_dir, target=dst, reason="install skill dir"))
    return items


def _materialize_skill_installs(plan: list[PlanItem], project_root: Path, kit_root: Path, *, pack: str, dest: str, dry_run: bool) -> None:
    # Not used yet; left as a future-safe hook.
    del plan, project_root, kit_root, pack, dest, dry_run
