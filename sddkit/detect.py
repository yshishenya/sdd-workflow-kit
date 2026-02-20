from __future__ import annotations

from pathlib import Path


def _exists(root: Path, rel: str) -> bool:
    return (root / rel).exists()


def detect_project(project_root: Path) -> dict[str, str]:
    """Detect the programming languages and package managers used in a project.
    
    This function analyzes the contents of the specified project_root directory to
    identify  the programming languages and package managers present. It checks for
    specific files  associated with various languages, such as `pyproject.toml` for
    Python, `package.json`  for Node.js, and `go.mod` for Go. Additionally, it
    evaluates the presence of certain  directories and files to determine the
    project's structure and recommends a profile  based on the findings.
    
    Args:
        project_root (Path): The path to the project directory to analyze.
    
    Returns:
        dict[str, str]: A dictionary containing detected languages, package managers,
        and other project characteristics.
    """
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
    has_speckit = _exists(project_root, ".specify/scripts") or _exists(project_root, ".specify/templates")

    langs = sorted(set(languages))
    recommended_profile = "generic"
    if has_speckit:
        recommended_profile = "speckit"
    elif has_meta_memory_bank or has_meta_sdd or has_meta_tools:
        recommended_profile = "memory_bank"

    return {
        "languages": ",".join(langs),
        "package_managers": ",".join(sorted(set(pms))),
        "has_github_actions": "true" if has_github else "false",
        "has_docker_compose": "true" if has_docker_compose else "false",
        "has_meta_memory_bank": "true" if has_meta_memory_bank else "false",
        "has_meta_sdd": "true" if has_meta_sdd else "false",
        "has_meta_tools": "true" if has_meta_tools else "false",
        "has_speckit": "true" if has_speckit else "false",
        "recommended_profile": recommended_profile,
    }
