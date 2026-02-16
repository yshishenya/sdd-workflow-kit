---
name: workflow-compliance
description: Ensure Codex follows project workflows and task-update rules (Memory Bank). Use when starting new tasks, when asked to follow a workflow/checklist/steps/definition of done, or when choosing between bug fix, new feature, refactor, or code review workflows.
---

# Workflow Compliance

## Workflow selection
- Identify task type: new feature, bug fix, refactor, code review, or other.
- If unclear, ask before making changes.

## Mandatory reads
- Read `meta/memory_bank/README.md` and follow its reading sequence.
- Load the relevant workflow file from `meta/memory_bank/workflows/`.

## Execution gate
- If any mandatory step cannot be completed, stop and ask for confirmation.

## Response checklist
- In the first response, state: `Workflow: <name>` and list the steps you will follow.
- In the final response, include a short checklist: Completed / Pending.

## Task updates
- Follow `meta/memory_bank/guides/task_updates.md`.
- Do not edit `meta/memory_bank/current_tasks.md` on feature/bugfix branches.

## Verification
- List required tests from the chosen workflow and whether they were run.
