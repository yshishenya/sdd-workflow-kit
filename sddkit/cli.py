from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .config import load_config, write_default_config
from .detect import detect_project
from .skills import import_codex_skills
from .sync import check_project, sync_project


def _abs(p: str | Path) -> Path:
    return Path(p).expanduser().resolve()


def _parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(prog="sdd-kit")
    sub = parser.add_subparsers(dest="cmd", required=True)

    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--project", default=".", help="Project root (default: .)")
    common.add_argument("--config", default=".sddkit/config.toml", help="Config path (relative to project root by default)")

    p_detect = sub.add_parser("detect", parents=[common], help="Detect project characteristics")

    p_bootstrap = sub.add_parser("bootstrap", parents=[common], help="Create config and sync managed scaffolding")
    p_bootstrap.add_argument("--locale", default=None, help="Template locale (en/ru). Overrides config for this run.")
    p_bootstrap.add_argument("--profile", default="auto", choices=["auto", "generic", "airis"], help="Config preset (auto/generic/airis). Used only when creating a new config.")

    p_sync = sub.add_parser("sync", parents=[common], help="Sync managed files (safe, idempotent)")
    p_sync.add_argument("--locale", default=None, help="Template locale (en/ru). Overrides config for this run.")
    p_sync.add_argument("--dry-run", action="store_true", help="Print plan, do not write")

    p_check = sub.add_parser("check", parents=[common], help="Check whether managed files are up to date")
    p_check.add_argument("--locale", default=None, help="Template locale (en/ru). Overrides config for this run.")
    p_check.add_argument("--fail-on-missing-config", default="false", help="true/false (default: false)")

    p_import = sub.add_parser("import-codex-skills", help="Import skills from CODEX_HOME into this repo skillpack")
    p_import.add_argument("--from", dest="from_dir", required=True, help="Source directory (e.g. ~/.codex/skills)")
    p_import.add_argument("--pack", default="codex", help="Pack name under skillpacks/ (default: codex)")
    p_import.add_argument("--kit-root", default=None, help="Kit repo root (defaults to auto-detect)")

    p_install = sub.add_parser("install-skills", parents=[common], help="Install skills from kit skillpack into project or global CODEX_HOME")
    p_install.add_argument("--pack", default="codex", help="Pack name under kit skillpacks/ (default: codex)")
    p_install.add_argument("--to", default="project", choices=["project", "global"], help="Install destination")
    p_install.add_argument("--dry-run", action="store_true", help="Print plan, do not write")

    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    ns = _parse_args(sys.argv[1:] if argv is None else argv)

    if ns.cmd == "import-codex-skills":
        from_dir = _abs(ns.from_dir)
        kit_root = _abs(ns.kit_root) if ns.kit_root else Path(__file__).resolve().parents[1]
        import_codex_skills(kit_root=kit_root, pack_name=ns.pack, source_dir=from_dir)
        return 0

    project_root = _abs(ns.project)
    config_path = Path(ns.config)
    if not config_path.is_absolute():
        config_path = project_root / config_path

    if ns.cmd == "detect":
        detection = detect_project(project_root)
        for k in sorted(detection.keys()):
            print(f"{k}={detection[k]}")
        return 0

    if ns.cmd == "bootstrap":
        if not config_path.exists():
            detection = detect_project(project_root)
            write_default_config(config_path, project_root=project_root, detection=detection, profile_override=ns.profile)
            print(f"Wrote {config_path}")
        cfg = load_config(config_path)
        locale = ns.locale or cfg.locale
        detection = detect_project(project_root)
        sync_project(project_root, config_path=config_path, cfg=cfg, detection=detection, locale=locale, dry_run=False)
        return 0

    if ns.cmd == "sync":
        cfg = load_config(config_path)
        locale = ns.locale or cfg.locale
        detection = detect_project(project_root)
        sync_project(project_root, config_path=config_path, cfg=cfg, detection=detection, locale=locale, dry_run=bool(ns.dry_run))
        return 0

    if ns.cmd == "check":
        fail_missing = str(ns.fail_on_missing_config).strip().lower() in {"1", "true", "yes", "y"}
        if not config_path.exists():
            msg = f"Config not found: {config_path}"
            if fail_missing:
                print(msg)
                return 2
            print(msg)
            print("Skipping (not bootstrapped). Run: sdd-kit bootstrap --project .")
            return 0
        cfg = load_config(config_path)
        locale = ns.locale or cfg.locale
        detection = detect_project(project_root)
        ok = check_project(project_root, config_path=config_path, cfg=cfg, detection=detection, locale=locale)
        return 0 if ok else 2

    if ns.cmd == "install-skills":
        cfg = load_config(config_path) if config_path.exists() else load_config(None)
        locale = getattr(ns, "locale", None) or cfg.locale
        detection = detect_project(project_root)
        sync_project(
            project_root,
            config_path=config_path,
            cfg=cfg,
            detection=detection,
            locale=locale,
            dry_run=bool(ns.dry_run),
            skills_install_pack=ns.pack,
            skills_install_to=ns.to,
            skills_install_only=True,
        )
        return 0

    raise AssertionError(f"Unhandled command: {ns.cmd}")
