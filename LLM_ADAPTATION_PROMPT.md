# LLM Prompt: Adapt Any Repo to This Kit

Copy/paste this to an LLM (Codex/Claude/etc) inside the target repository.

---

Goal: pull `sdd-workflow-kit` into this repo and auto-bootstrap the workflow scaffolding without breaking existing CI.

Constraints:

- Do not overwrite existing unmanaged files.
- Prefer additive changes (new files) over modifying existing ones.
- If `.github/workflows/` exists, add a new check workflow only (do not edit existing workflows).

Steps:

1. Add the kit to the repo (recommended: git submodule):
   - `git submodule add <KIT_GIT_URL> .tooling/sdd-workflow-kit`

2. Bootstrap (creates `.sddkit/config.toml` if missing, then syncs managed files):
   - `python3 .tooling/sdd-workflow-kit/bin/sdd-kit bootstrap --project .`

3. Open `.sddkit/config.toml` and confirm:
   - `[sddkit] profile` (`generic`, `memory_bank`, or `speckit`)
   - `[project] name` and `integration_branch`
   - `[manage]` toggles (speckit/memory_bank/docs/specs, plus optional meta_* / codex_scaffold)
   - `[github] kit_path` matches `.tooling/sdd-workflow-kit`

4. Apply sync again (idempotent):
   - `python3 .tooling/sdd-workflow-kit/bin/sdd-kit sync --project .`

5. If the repo needs project-local skills:
   - `python3 .tooling/sdd-workflow-kit/bin/sdd-kit install-skills --project . --to project`

6. Verify drift locally:
   - `python3 .tooling/sdd-workflow-kit/bin/sdd-kit check --project .`

Result expectations:

- `AGENTS.md` exists and points to the Memory Bank (if enabled).
- Memory Bank scaffold exists (default: `meta/memory_bank/*`) when enabled.
- SDD scaffold exists (default: `meta/sdd/*`) when enabled.
- Meta tools exist (default: `meta/tools/*`) and scripts are executable when enabled.
- `.github/workflows/sdd-kit-check.yml` exists (if GitHub Actions present).

If conflicts appear:

- Do not overwrite. Disable the conflicting manager in `.sddkit/config.toml` or move the kit-managed path.
- Use `.sddkit/fragments/AGENTS.append.md` to add local agent notes without editing the managed `AGENTS.md`.
