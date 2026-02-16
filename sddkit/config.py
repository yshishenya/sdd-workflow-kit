from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

try:
    import tomllib  # pyright: ignore[reportMissingImports]
except Exception:  # pragma: no cover
    tomllib = None  # type: ignore[assignment]


@dataclass(frozen=True)
class SddKitConfig:
    locale: str = "en"
    safe_mode: bool = True
    profile: str = "auto"  # auto|generic|airis
    project_name: str = "Project"
    integration_branch: str = "main"
    is_fork: bool = False
    upstream_project: str = "Open WebUI"

    docs_root: str = "docs"
    specs_root: str = "specs"
    memory_bank_root: str = "meta/memory_bank"
    meta_tools_root: str = "meta/tools"
    meta_sdd_root: str = "meta/sdd"
    codex_root: str = ".codex"

    manage_agents_md: bool = True
    manage_github_workflow: bool = True
    manage_docs_scaffold: bool = True
    manage_specs_scaffold: bool = True
    manage_memory_bank: bool = False
    manage_meta_tools: bool = False
    manage_meta_sdd: bool = False
    manage_codex_scaffold: bool = False

    skills_default_pack: str = "codex"
    skills_default_install_to: str = "project"  # project|global
    github_kit_path: str = ".tooling/sdd-workflow-kit"
    github_config_path: str = ".sddkit/config.toml"
    github_fail_on_missing_config: bool = False


DEFAULT_CONFIG = SddKitConfig()


def _deep_get(d: dict[str, Any], path: str, default: Any) -> Any:
    cur: Any = d
    for part in path.split("."):
        if not isinstance(cur, dict) or part not in cur:
            return default
        cur = cur[part]
    return cur


def load_config(config_path: Path | None) -> SddKitConfig:
    if config_path is None or not config_path.exists():
        return DEFAULT_CONFIG
    if tomllib is None:
        raise RuntimeError("tomllib is not available; use Python 3.11+ or switch config format.")
    raw = tomllib.loads(config_path.read_text(encoding="utf-8"))

    cfg = SddKitConfig(
        locale=str(_deep_get(raw, "sddkit.locale", DEFAULT_CONFIG.locale)),
        safe_mode=bool(_deep_get(raw, "sddkit.safe_mode", DEFAULT_CONFIG.safe_mode)),
        profile=str(_deep_get(raw, "sddkit.profile", DEFAULT_CONFIG.profile)),
        project_name=str(_deep_get(raw, "project.name", DEFAULT_CONFIG.project_name)),
        integration_branch=str(_deep_get(raw, "project.integration_branch", DEFAULT_CONFIG.integration_branch)),
        is_fork=bool(_deep_get(raw, "project.is_fork", DEFAULT_CONFIG.is_fork)),
        upstream_project=str(_deep_get(raw, "project.upstream_project", DEFAULT_CONFIG.upstream_project)),
        docs_root=str(_deep_get(raw, "paths.docs_root", DEFAULT_CONFIG.docs_root)),
        specs_root=str(_deep_get(raw, "paths.specs_root", DEFAULT_CONFIG.specs_root)),
        memory_bank_root=str(_deep_get(raw, "paths.memory_bank_root", DEFAULT_CONFIG.memory_bank_root)),
        meta_tools_root=str(_deep_get(raw, "paths.meta_tools_root", DEFAULT_CONFIG.meta_tools_root)),
        meta_sdd_root=str(_deep_get(raw, "paths.meta_sdd_root", DEFAULT_CONFIG.meta_sdd_root)),
        codex_root=str(_deep_get(raw, "paths.codex_root", DEFAULT_CONFIG.codex_root)),
        manage_agents_md=bool(_deep_get(raw, "manage.agents_md", DEFAULT_CONFIG.manage_agents_md)),
        manage_github_workflow=bool(_deep_get(raw, "manage.github_workflow", DEFAULT_CONFIG.manage_github_workflow)),
        manage_docs_scaffold=bool(_deep_get(raw, "manage.docs_scaffold", DEFAULT_CONFIG.manage_docs_scaffold)),
        manage_specs_scaffold=bool(_deep_get(raw, "manage.specs_scaffold", DEFAULT_CONFIG.manage_specs_scaffold)),
        manage_memory_bank=bool(_deep_get(raw, "manage.memory_bank", DEFAULT_CONFIG.manage_memory_bank)),
        manage_meta_tools=bool(_deep_get(raw, "manage.meta_tools", DEFAULT_CONFIG.manage_meta_tools)),
        manage_meta_sdd=bool(_deep_get(raw, "manage.meta_sdd", DEFAULT_CONFIG.manage_meta_sdd)),
        manage_codex_scaffold=bool(_deep_get(raw, "manage.codex_scaffold", DEFAULT_CONFIG.manage_codex_scaffold)),
        skills_default_pack=str(_deep_get(raw, "skills.default_pack", DEFAULT_CONFIG.skills_default_pack)),
        skills_default_install_to=str(_deep_get(raw, "skills.default_install_to", DEFAULT_CONFIG.skills_default_install_to)),
        github_kit_path=str(_deep_get(raw, "github.kit_path", DEFAULT_CONFIG.github_kit_path)),
        github_config_path=str(_deep_get(raw, "github.config", DEFAULT_CONFIG.github_config_path)),
        github_fail_on_missing_config=bool(_deep_get(raw, "github.fail_on_missing_config", DEFAULT_CONFIG.github_fail_on_missing_config)),
    )
    return cfg


def write_default_config(config_path: Path, *, project_root: Path, detection: dict[str, Any]) -> None:
    config_path.parent.mkdir(parents=True, exist_ok=True)
    # Keep config minimal and stable; detection is informational.
    locale = os.environ.get("SDDKIT_LOCALE", "en")
    project_name = project_root.name
    profile = str(detection.get("recommended_profile") or "generic")
    integration_branch = "airis_b2c" if profile == "airis" else "main"
    manage_memory_bank = "true" if profile == "airis" else "false"
    manage_meta_tools = "true" if profile == "airis" else "false"
    manage_meta_sdd = "true" if profile == "airis" else "false"
    manage_docs_scaffold = "false" if profile == "airis" else "true"
    manage_specs_scaffold = "false" if profile == "airis" else "true"
    content = f"""[sddkit]
locale = "{locale}"
safe_mode = true
profile = "{profile}"

[project]
name = "{project_name}"
integration_branch = "{integration_branch}"
is_fork = false
upstream_project = "Open WebUI"

[paths]
docs_root = "docs"
specs_root = "specs"
memory_bank_root = "meta/memory_bank"
meta_tools_root = "meta/tools"
meta_sdd_root = "meta/sdd"
codex_root = ".codex"

[manage]
agents_md = true
github_workflow = true
docs_scaffold = {manage_docs_scaffold}
specs_scaffold = {manage_specs_scaffold}
memory_bank = {manage_memory_bank}
meta_tools = {manage_meta_tools}
meta_sdd = {manage_meta_sdd}
codex_scaffold = false

[skills]
default_pack = "codex"
default_install_to = "project"

[github]
kit_path = ".tooling/sdd-workflow-kit"
config = ".sddkit/config.toml"
fail_on_missing_config = false

[detection]
languages = "{detection.get('languages', '')}"
package_managers = "{detection.get('package_managers', '')}"
"""
    config_path.write_text(content, encoding="utf-8")
