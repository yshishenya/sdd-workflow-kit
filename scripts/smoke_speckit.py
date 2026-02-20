#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


def run(cmd: list[str], *, cwd: Path, env: dict[str, str] | None = None) -> None:
    print("+", " ".join(cmd))
    subprocess.run(cmd, cwd=str(cwd), env=env, check=True)


def run_capture(cmd: list[str], *, cwd: Path) -> str:
    print("+", " ".join(cmd))
    return subprocess.check_output(cmd, cwd=str(cwd), text=True)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--keep", action="store_true", help="Keep the temporary repo directory on success/failure")
    ns = ap.parse_args()

    kit_root = Path(__file__).resolve().parents[1]
    kit_cli = kit_root / "bin" / "sdd-kit"
    if not kit_cli.exists():
        raise FileNotFoundError(f"Expected kit CLI at {kit_cli}")
    kit_sha = (
        subprocess.run(["git", "rev-parse", "HEAD"], cwd=str(kit_root), check=True, capture_output=True, text=True)
        .stdout.strip()
    )

    tmp_root = Path(tempfile.mkdtemp(prefix="sddkit-speckit-smoke-"))
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

        project_kit = repo / ".tooling" / "sdd-workflow-kit"
        project_cli = project_kit / "bin" / "sdd-kit"
        # Ensure the submodule checkout matches this working tree's HEAD (so the smoke test
        # validates unmerged changes on a feature branch).
        run(["git", "checkout", kit_sha], cwd=project_kit)

        # Bootstrap and sync Spec Kit mode.
        run(
            [
                sys.executable,
                str(project_cli),
                "bootstrap",
                "--project",
                ".",
                "--profile",
                "speckit",
                "--locale",
                "en",
            ],
            cwd=repo,
        )
        run([sys.executable, str(project_cli), "sync", "--project", "."], cwd=repo)

        # Validate installed files exist.
        required_skills = [
            repo / ".specify" / "templates" / "spec-template.md",
            repo / ".specify" / "templates" / "plan-template.md",
            repo / ".specify" / "scripts" / "bash" / "create-new-feature.sh",
            repo / ".codex" / "skills" / "speckit-specify" / "SKILL.md",
            repo / ".codex" / "skills" / "speckit-plan" / "SKILL.md",
            repo / ".codex" / "skills" / "speckit-tasks" / "SKILL.md",
            repo / ".codex" / "skills" / "speckit-implement" / "SKILL.md",
            repo / ".codex" / "skills" / "speckit-planreview" / "SKILL.md",
        ]
        required_prompts = [
            repo / ".specify" / "templates" / "spec-template.md",
            repo / ".specify" / "templates" / "plan-template.md",
            repo / ".specify" / "scripts" / "bash" / "create-new-feature.sh",
            repo / ".codex" / "prompts" / "speckit.specify.md",
            repo / ".codex" / "prompts" / "speckit.plan.md",
            repo / ".codex" / "prompts" / "speckit.planreview.md",
            repo / ".codex" / "prompts" / "speckit.tasks.md",
            repo / ".codex" / "prompts" / "speckit.implement.md",
        ]

        required = required_skills
        if (repo / ".codex" / "skills").exists():
            required = required_skills
        elif (repo / ".codex" / "prompts").exists():
            required = required_prompts

        missing = [p for p in required if not p.exists()]
        if missing:
            raise RuntimeError("Missing expected files:\n" + "\n".join(str(p) for p in missing))

        # Validate core Spec Kit scripts work (no agent required).
        out = run_capture(
            ["bash", str(repo / ".specify" / "scripts" / "bash" / "create-new-feature.sh"), "--json", "Test feature"],
            cwd=repo,
        )
        feature_info = json.loads(out.strip().splitlines()[-1])
        branch = feature_info.get("BRANCH_NAME", "")
        spec_file = Path(feature_info.get("SPEC_FILE", ""))
        if not branch or not spec_file.exists():
            raise RuntimeError(f"Feature creation failed: branch={branch!r} spec_file={spec_file}")

        out = run_capture(
            ["bash", str(repo / ".specify" / "scripts" / "bash" / "setup-plan.sh"), "--json"],
            cwd=repo,
        )
        plan_info = json.loads(out.strip().splitlines()[-1])
        impl_plan = Path(plan_info.get("IMPL_PLAN", ""))
        if not impl_plan.exists():
            raise RuntimeError(f"Plan setup failed: {impl_plan}")

        # Generate/update AGENTS.md via Spec Kit script, then verify our overlay manual block survives updates.
        run(["bash", str(repo / ".specify" / "scripts" / "bash" / "update-agent-context.sh"), "codex"], cwd=repo)

        sentinel = "SMOKE-SPECKIT-MANUAL-BLOCK"
        overlay_path = repo / ".sddkit" / "fragments" / "AGENTS.manual.md"
        overlay_path.write_text(
            "# Local additions for AGENTS.md\n\n- "
            + sentinel
            + "\n",
            encoding="utf-8",
        )
        run([sys.executable, str(project_cli), "sync", "--project", "."], cwd=repo)
        agents_text = (repo / "AGENTS.md").read_text(encoding="utf-8", errors="replace")
        if sentinel not in agents_text:
            raise RuntimeError("AGENTS.md manual block overlay was not applied (sentinel missing)")

        run(["bash", str(repo / ".specify" / "scripts" / "bash" / "update-agent-context.sh"), "codex"], cwd=repo)
        agents_text2 = (repo / "AGENTS.md").read_text(encoding="utf-8", errors="replace")
        if sentinel not in agents_text2:
            raise RuntimeError("AGENTS.md manual block was not preserved after update-agent-context (sentinel missing)")

        out = run_capture(
            ["bash", str(repo / ".specify" / "scripts" / "bash" / "check-prerequisites.sh"), "--json"],
            cwd=repo,
        )
        _ = json.loads(out.strip().splitlines()[-1])

        # Drift check should pass.
        run([sys.executable, str(project_cli), "check", "--project", "."], cwd=repo)

        print("OK: Spec Kit hybrid install + scripts + drift check")
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
