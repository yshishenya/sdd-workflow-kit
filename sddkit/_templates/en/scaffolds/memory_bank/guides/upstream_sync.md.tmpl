# Upstream Sync (Open WebUI) — Conflict-Minimizing Rules

Airis is a fork of Open WebUI. We periodically integrate upstream changes. This guide describes how to keep the fork easy to rebase/merge.

## Principles

1. **Keep diffs small**: the fewer lines we touch in upstream-owned files, the fewer conflicts during updates.
2. **Prefer additive**: add new files/modules rather than editing existing upstream files.
3. **Thin hooks**: when upstream files must change, keep them as a thin wrapper that delegates to fork-owned code.
4. **No formatting churn** in upstream-owned files (avoid “drive-by” cleanup).

## “Fork-owned” vs “Upstream-owned”

Practical rule of thumb:

- Fork-owned (safe to change freely): `meta/memory_bank/**`, `.codex/**`, new `src/lib/utils/airis/**` modules, and other clearly Airis-specific additions.
- Upstream-owned (treat as stable surface): most existing app/runtime code under `backend/` and `src/` unless explicitly introduced for Airis.

When in doubt: assume a file is upstream-owned and minimize edits.

## Required documentation for non-trivial changes

For every non-trivial work item:

- Create a work item spec: `meta/memory_bank/specs/work_items/YYYY-MM-DD__<type>__<slug>.md`
- Include an **Upstream impact** section:
  - list upstream-owned files touched
  - why it was necessary (no extension point / missing hook)
  - how the change was minimized (thin hook, additive helper, guarded behavior)

## Recommended structure for minimizing upstream conflicts

- Frontend: isolate fork logic in `src/lib/utils/airis/*` (or other clearly Airis-namespaced modules) and keep upstream components as callers.
- Backend: prefer small helpers in `backend/open_webui/utils/` (create `backend/open_webui/utils/airis/` when it helps isolate functionality).

## Operational workflow for upstream updates (high-level)

1. Do upstream sync work on a dedicated branch (from integration branch), e.g. `chore/upstream-sync-YYYY-MM-DD`.
2. Integrate upstream changes (merge or rebase per team policy).
3. Resolve conflicts by preserving upstream intent and re-applying Airis changes via thin hooks where possible.
4. Run the fastest meaningful verification (Docker Compose-first).
5. Record a short entry in `meta/memory_bank/current_tasks.md` describing the sync and any high-risk conflict resolutions.

