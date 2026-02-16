# Universal AI-Assisted Development Workflow (Reusable)

This guide captures a **stable, reusable workflow** for building software with LLM assistants/agents while keeping the system safe, reviewable, and verifiable.

## Key Idea

**LLMs accelerate generation, not correctness.** Your process must minimize *verification debt*:

- Small batches (small diffs, frequent integration)
- Explicit acceptance criteria
- Strong verification gates (tests, lint, typecheck, security review)
- Clear audit trail (specs, decisions, task logs)

## Directory Convention (Single Root)

To keep artifacts discoverable and avoid “docs sprawl”, keep all process/spec/docs/tools under a single directory:

- `META_ROOT/` (in this repo: `meta/`)

Recommended universal names for other repos:

- `meta/` (short, explicit, visible)
- `project/` (simple, visible)
- `.project/` (hidden metadata; sometimes less discoverable)
- `workflow/` (explicit, but may feel “process-heavy”)

Structure:

- `META_ROOT/memory_bank/` — rules, patterns, workflows, work item specs, task logs
- `META_ROOT/sdd/` — SDD specs + SDD usage docs
- `META_ROOT/docs/` — project-specific docs (architecture/guides/reference)
- `META_ROOT/tools/` — helper scripts + wrappers

## Artifact Types (What To Write)

### 1) Work Item Spec (MD, narrative)

Use for any **non-trivial** change.

Contains:
- Context + goal
- Acceptance criteria
- Non-goals
- Scope (backend/frontend/config/data)
- Upstream impact (if relevant)
- Verification plan
- Rollback

### 2) SDD Spec (JSON, structured execution plan)

Use for any **non-trivial** change.

Contains:
- Phases/tasks
- Dependencies/blockers
- Verification nodes (auto/manual/fidelity)

Rule: cross-link MD <-> JSON so neither becomes orphaned.

### 3) Branch Updates (log, conflict-free)

Never edit a shared “current tasks” file on feature branches.
Append to a per-branch (or per-day) log and consolidate on integration/mainline branch.

## Risk Tiering (Keeps Process Lightweight)

### Trivial (low risk)

- No spec required
- Still: small diff + at least one relevant check (unit test, lint, or manual verification)

### Non-trivial (default)

- Work item spec (MD) + SDD spec (JSON)
- Docker-first verification (tests + lint + typecheck as applicable)

### High risk (auth/billing/security/agent actions)

Do everything in non-trivial, plus:
- Threat model notes (what can go wrong, how we mitigate)
- “Second brain” review: have a second agent or a human do an adversarial review
- Add negative/abuse-case tests (not only happy path)

## Universal Workflow (Step-By-Step)

1. **Start**
   - Read `AGENTS.md` (repo guardrails)
   - Read `META_ROOT/memory_bank/README.md` (mandatory sequence)
   - Identify task type: bugfix / feature / refactor / docs

2. **Discover**
   - Find existing code/patterns first (avoid reinventing)
   - Confirm current versions in `META_ROOT/memory_bank/tech_stack.md` + lockfiles
   - For unfamiliar libraries/providers: confirm the repo-pinned version, then read the official docs for that version
     (or latest docs + release notes if docs aren't versioned)

3. **Specify (for non-trivial)**
   - Write work item spec (MD)
   - Create SDD spec (JSON) and break down to small executable tasks
   - Define verification plan (what to run, what to check manually)

4. **Implement in Small Batches**
   - Make the smallest change that moves the spec forward
   - Keep diffs reviewable
   - Prefer additive modules + thin hooks over invasive edits (esp. in forked repos)

5. **Verify**
   - Run the narrowest meaningful test suite first
   - Then widen (full suite) for risky areas
   - For LLM-facing behavior: add/extend evals (golden tests) and run them before merge
   - Ensure logs do not contain secrets/PII

6. **Review**
   - Self-review checklist (behavior, tests, security, docs)
   - For high-risk: get an explicit second review (agent or human)

7. **Document + Track**
   - Update relevant guides/patterns if this change taught us something new
   - Append status to branch updates; consolidate on integration/mainline

## LLM-Specific Guardrails (Add To Any Repo)

- Treat AI output as **untrusted** until verified (tests + review).
- Prefer “spec + tests” over “prompt-only” correctness.
- Treat prompts/tool policies as code artifacts: version them, review them, test them.
- For agent/tooling features: explicitly consider prompt-injection and data exfiltration risks.

## Evals (LLM Regression Testing)

If your change affects prompts, routing, tools, retrieval, or any “AI decision” logic, treat it like a public API change:

- Add a small eval set (happy path + edge cases + adversarial inputs).
- Make evals deterministic where possible (fixed seeds, cached fixtures, temperature 0 for tests).
- Track eval results over time to catch regressions early.

## What “Ideal” Means (Definition of Done)

- Acceptance criteria satisfied
- Verification evidence recorded (commands + outcomes)
- No accidental breaking changes
- No secrets/PII leakage
- Documentation updated where future-you would look first
- Diff is small enough to review quickly

## Further Reading (External)

- DORA Capabilities:
  - Working in small batches: https://dora.dev/capabilities/working-in-small-batches/
  - Trunk-based development: https://dora.dev/capabilities/trunk-based-development/
  - Continuous Integration: https://dora.dev/devops-capabilities/technical/continuous-integration/
- OWASP Top 10 for LLM Applications: https://owasp.org/www-project-top-10-for-large-language-model-applications/
- NIST AI Risk Management Framework (AI RMF 1.0): https://www.nist.gov/itl/ai-risk-management-framework
- Google Secure AI Framework (SAIF): https://saif.google/
- OpenAI Evals (open-source): https://github.com/openai/evals
- OpenAI evaluation best practices: https://platform.openai.com/docs/guides/evals/evaluation-best-practices
- GitHub Copilot:
  - Best practices: https://docs.github.com/en/copilot/get-started/best-practices
  - Coding agent best practices: https://docs.github.com/en/copilot/using-github-copilot/using-github-copilot-coding-agent/best-practices-for-using-github-copilot-to-work-on-tasks
  - Responsible use: https://docs.github.com/en/copilot/responsible-use
- Anthropic prompt engineering overview: https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/overview
