from __future__ import annotations

from pathlib import Path


def _exists(root: Path, rel: str) -> bool:
    return (root / rel).exists()


def detect_project(project_root: Path) -> dict[str, str]:
    languages: list[str] = []
    pms: list[str] = []

    if _exists(project_root, "pyproject.toml") or _exists(project_root, "requirements.txt") or _exists(project_root, "uv.lock"):
        languages.append("python")
        if _exists(project_root, "uv.lock"):
            pms.append("uv")
        elif _exists(project_root, "poetry.lock"):
            pms.append("poetry")
        else:
            pms.append("pip")

    if _exists(project_root, "package.json"):
        languages.append("node")
        if _exists(project_root, "pnpm-lock.yaml"):
            pms.append("pnpm")
        elif _exists(project_root, "yarn.lock"):
            pms.append("yarn")
        elif _exists(project_root, "bun.lockb"):
            pms.append("bun")
        else:
            pms.append("npm")

    if _exists(project_root, "go.mod"):
        languages.append("go")
        pms.append("go")

    if _exists(project_root, "Cargo.toml"):
        languages.append("rust")
        pms.append("cargo")

    if not languages:
        languages.append("unknown")

    has_github = _exists(project_root, ".github/workflows")
    has_docker_compose = _exists(project_root, "docker-compose.yaml") or _exists(project_root, "compose.yaml") or _exists(project_root, "compose.yml")
    has_backend_dir = _exists(project_root, "backend")
    has_src_dir = _exists(project_root, "src")

    has_meta_memory_bank = _exists(project_root, "meta/memory_bank/README.md")
    has_meta_sdd = _exists(project_root, "meta/sdd/README.md") or _exists(project_root, "meta/sdd/specs")
    has_meta_tools = _exists(project_root, "meta/tools")

    langs = sorted(set(languages))
    recommended_profile = "generic"
    if has_meta_memory_bank or has_meta_sdd or has_meta_tools:
        recommended_profile = "airis"
    elif has_docker_compose and has_backend_dir and has_src_dir and ("python" in langs) and ("node" in langs):
        recommended_profile = "airis"

    return {
        "languages": ",".join(langs),
        "package_managers": ",".join(sorted(set(pms))),
        "has_github_actions": "true" if has_github else "false",
        "has_docker_compose": "true" if has_docker_compose else "false",
        "has_meta_memory_bank": "true" if has_meta_memory_bank else "false",
        "has_meta_sdd": "true" if has_meta_sdd else "false",
        "has_meta_tools": "true" if has_meta_tools else "false",
        "recommended_profile": recommended_profile,
    }
