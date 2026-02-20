#!/usr/bin/env python3
from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


def run(cmd: list[str], *, cwd: Path) -> None:
    print("+", " ".join(cmd))
    subprocess.run(cmd, cwd=str(cwd), check=True)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--keep", action="store_true", help="Keep the temporary repo directory on success/failure")
    ns = ap.parse_args()

    kit_root = Path(__file__).resolve().parents[1]

    tmp_root = Path(tempfile.mkdtemp(prefix="sddkit-memory-bank-smoke-"))
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

        run(
            [
                sys.executable,
                str(project_cli),
                "bootstrap",
                "--project",
                ".",
                "--profile",
                "memory_bank",
                "--locale",
                "en",
            ],
            cwd=repo,
        )
        run([sys.executable, str(project_cli), "check", "--project", "."], cwd=repo)

        required = [
            repo / "AGENTS.md",
            repo / "meta" / "memory_bank" / "README.md",
            repo / "meta" / "memory_bank" / "tech_stack.md",
            repo / "meta" / "memory_bank" / "current_tasks.md",
        ]
        missing = [p for p in required if not p.exists()]
        if missing:
            raise RuntimeError("Missing expected files:\n" + "\n".join(str(p) for p in missing))

        print("OK: memory_bank profile bootstrap + drift check")
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

