#!/usr/bin/env python3
from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


def run(cmd: list[str], *, cwd: Path) -> None:
    """Execute a command in a specified directory."""
    print("+", " ".join(cmd))
    subprocess.run(cmd, cwd=str(cwd), check=True)


def main() -> int:
    """Run the main process for bootstrapping the Airis profile.
    
    This function initializes a temporary Git repository, configures it,  and adds
    the sdd-workflow-kit as a submodule. It then bootstraps the  project using the
    specified Airis profile and checks for required files.  If any expected files
    are missing or if the necessary executables are  not set, it raises an error.
    The temporary directory can be kept for  debugging based on the command-line
    argument provided.
    """
    ap = argparse.ArgumentParser()
    ap.add_argument("--keep", action="store_true", help="Keep the temporary repo directory on success/failure")
    ns = ap.parse_args()

    kit_root = Path(__file__).resolve().parents[1]

    tmp_root = Path(tempfile.mkdtemp(prefix="sddkit-airis-smoke-"))
    repo = tmp_root / "repo"
    repo.mkdir(parents=True, exist_ok=True)

    try:
        run(["git", "init"], cwd=repo)
        run(["git", "config", "user.email", "smoke@example.com"], cwd=repo)
        run(["git", "config", "user.name", "Smoke Test"], cwd=repo)

        # Add this kit as a submodule (local path). Git may block file:// by default.
        run(
            [
                "git",
                "-c",
                "protocol.file.allow=always",
                "submodule",
                "add",
                str(kit_root),
                ".tooling/sdd-workflow-kit",
            ],
            cwd=repo,
        )
        run(["git", "commit", "-m", "Add sdd-workflow-kit submodule"], cwd=repo)
        run(["git", "submodule", "update", "--init", "--recursive"], cwd=repo)

        project_cli = repo / ".tooling" / "sdd-workflow-kit" / "bin" / "sdd-kit"

        # Airis profile = memory_bank + meta tools + meta/sdd + codex scaffolds + AGENTS.md.
        # Use ru locale to verify fallback-to-en for scaffolds that are not translated.
        run(
            [
                sys.executable,
                str(project_cli),
                "bootstrap",
                "--project",
                ".",
                "--profile",
                "airis",
                "--locale",
                "ru",
            ],
            cwd=repo,
        )
        run([sys.executable, str(project_cli), "check", "--project", "."], cwd=repo)

        required = [
            repo / "AGENTS.md",
            repo / "meta" / "memory_bank" / "README.md",
            repo / "meta" / "memory_bank" / "tech_stack.md",
            repo / "meta" / "tools" / "sdd",
            repo / "meta" / "sdd" / "README.md",
            repo / ".codex" / "environments" / "environment.toml",
        ]
        missing = [p for p in required if not p.exists()]
        if missing:
            raise RuntimeError("Missing expected files:\n" + "\n".join(str(p) for p in missing))

        # The meta/tools/sdd wrapper should be executable.
        if not (repo / "meta" / "tools" / "sdd").stat().st_mode & 0o111:
            raise RuntimeError("Expected meta/tools/sdd to be executable")

        print("OK: Airis profile (memory_bank + meta/*) bootstrap + drift check")
        if ns.keep:
            print(f"Kept: {tmp_root}")
        else:
            shutil.rmtree(tmp_root)
        return 0

    except Exception:
        if ns.keep:
            print(f"Kept for debugging: {tmp_root}", file=sys.stderr)
        else:
            shutil.rmtree(tmp_root, ignore_errors=True)
        raise


if __name__ == "__main__":
    raise SystemExit(main())

