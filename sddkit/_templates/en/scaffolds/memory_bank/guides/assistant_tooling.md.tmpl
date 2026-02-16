# Assistant Tooling (Codex)

This repository is **Codex-first**: assume the assistant runs commands via **Docker Compose**, not via local Python/npm.

## Canonical sources (and how they connect)

- **Rules**: `AGENTS.md` (project root)
  - Defines mandatory Memory Bank reads, workflow gate, and “no blocking I/O” rules.
- **Memory Bank**: `meta/memory_bank/README.md`
  - Mandatory reading sequence + links to workflows/guides/patterns.
- **Codex environment**: `.codex/environments/environment.toml`
  - Docker-first setup and the Codex “Actions” for tests/linters and stack lifecycle.
- **Compose files**
  - Base: `docker-compose.yaml`
  - Dev overlay (HMR/reload): `docker-compose.dev.yaml`
  - Codex helpers: `.codex/docker-compose.codex.yaml` (e.g. `pytools`, `e2e`)
- **Manual helper (optional)**: `scripts/dev_stack.sh`
  - Interactive menu for humans; uses the same compose file pair.

## Docker-first rule (important)

- Prefer **compose-run** commands (or Codex Actions) for:
  - Backend (compose service `airis`): `pytest`, `black`, `ruff`/`mypy` (via `pytools`)
  - Frontend: `npm run test:frontend`, `npm run check`, `npm run lint:frontend`
  - E2E: `npm run test:e2e`
- Avoid creating a local `.venv` for assistant runs unless explicitly requested.

## Shortcuts (package.json)

For convenience (and to reduce command drift), `package.json` provides Docker Compose wrappers:

- Backend: `npm run docker:test:backend`, `npm run docker:format:backend`, `npm run docker:lint:backend`
- Frontend: `npm run docker:test:frontend`, `npm run docker:check:frontend`, `npm run docker:lint:frontend`, `npm run docker:format:frontend`
- E2E: `npm run docker:test:e2e`

## Docs checks (optional but recommended)

- Markdown internal links: `python3 meta/tools/check_markdown_links.py`

## Knowledge persistence

- Solutions log: `meta/docs/solutions/` (templates + patterns)

## Worktrees note

- Codex worktrees may live outside the repo (e.g. `~/.codex/worktrees/...`).
- Do not assume fixed relative paths; rely on `$PWD` (or `${wt}` when defined) and compose file paths relative to the worktree root.

## SDD toolkit (optional)

If you use the SDD (Spec-Driven Development) toolkit, project-local config lives under `.claude/`:

- `.claude/settings.local.json` (permissions)
- `.claude/git_config.json` (git integration behaviour)
- `.claude/sdd_config.json` (SDD CLI output preferences)

Note: these files are **local machine config** and are listed in `.claude/.gitignore` (not committed).
For day-to-day SDD commands in this repo, always use the wrapper:

- `meta/tools/sdd ...`
