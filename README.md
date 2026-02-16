# sdd-workflow-kit

Universal repo you can pull into any project to bootstrap and keep in sync:

- `AGENTS.md` (agent instructions + skill registry)
- SDD scaffolding (`docs/templates/*`, `docs/Architecture/*`, `docs/ADR/*`, `docs/Features/*`, `specs/*`)
- Memory Bank scaffolding (optional, Airis-style: `meta/memory_bank/*`)
- Meta SDD scaffolding (optional: `meta/sdd/*` + wrapper `meta/tools/sdd`)
- GitHub Actions check workflow (non-invasive, adds new workflow only)
- Optional Codex skills packaging (imports from `~/.codex/skills` into this repo, then can install elsewhere)

## What "safe" means

- The kit only writes files it **manages** (it adds a `managed-by: sdd-workflow-kit` header).
- If a file already exists and is **not** managed, `sync` will **skip** it.
- `check` will **fail** on files that should be managed but are not (so you notice conflicts early).

## Quick start (inside a target project)

1. Add this repo as a submodule (recommended path):
   - `git submodule add <YOUR_GIT_URL> .tooling/sdd-workflow-kit`

2. Bootstrap the project (safe defaults: never overwrite unmanaged files):
   - `python3 .tooling/sdd-workflow-kit/bin/sdd-kit bootstrap --project .`
   - If you want Memory Bank + `meta/*` scaffolds in a new repo: `python3 .tooling/sdd-workflow-kit/bin/sdd-kit bootstrap --project . --profile airis`

3. Keep files up to date:
   - `python3 .tooling/sdd-workflow-kit/bin/sdd-kit sync --project .`

4. CI drift check (optional): commit the generated workflow
   - `.github/workflows/sdd-kit-check.yml`

## Configure per-project

Edit `.sddkit/config.toml`:

- Disable anything you don't want managed (example: if you already have a hand-written `AGENTS.md`):
  - `[manage] agents_md = false`
- Change where the kit lives in the repo:
  - `[github] kit_path = ".tooling/sdd-workflow-kit"`
- Decide whether CI should fail when the kit is not bootstrapped:
  - `[github] fail_on_missing_config = false`

Add local agent instructions without touching the managed file:

- `.sddkit/fragments/AGENTS.append.md`

## Quick start (build your org skillpack once)

Import your currently installed Codex skills into this repo:

- `python3 bin/sdd-kit import-codex-skills --from /Users/$USER/.codex/skills --pack codex`

This will populate `skillpacks/codex/skills/*` so the kit becomes self-contained.

Install that skillpack into a project (project-local) or into CODEX_HOME (global):

- Project: `python3 .tooling/sdd-workflow-kit/bin/sdd-kit install-skills --project . --to project`
- Global: `python3 .tooling/sdd-workflow-kit/bin/sdd-kit install-skills --project . --to global`

## Design principles

- Idempotent: running `sync` multiple times is safe.
- Non-destructive: never overwrites files it does not manage.
- Managed marker: generated files include `managed-by: sdd-workflow-kit` in the header.
- Extensible: templates and profiles live in `sddkit/_templates/`.
