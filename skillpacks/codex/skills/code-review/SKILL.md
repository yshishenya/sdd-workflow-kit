---
name: code-review
description: General-purpose code review workflow and checklist for reviewing PRs, diffs, or code changes. Use when asked to do a code review, review a PR/diff, or requested "code review", "code rewiew", "сделай ревью", or "ревью"; focus on correctness, security, testing, performance, and documentation readiness.
---

# Code Review

## Overview

Provide a structured review process and a comprehensive checklist to assess code quality, risk, and readiness for merge.

## Workflow

1. Gather inputs: diff/PR, scope, requirements, and test results; ask for missing context.
2. Triage risk: correctness, security, data loss, migrations, and backward compatibility.
3. Review by area using the reference checklist (architecture, code quality, async, testing, docs).
4. Report findings with severity, file/line references, and clear recommendations.
5. Close with questions/assumptions, a brief summary, and verification steps.

## Output Format

- List findings first, ordered by severity.
- For each finding, include issue, impact, location, and fix recommendation.
- Follow with open questions/assumptions.
- End with a brief readiness summary and suggested tests.

## Reference Checklist

Load `references/code-review-process.md` and apply the relevant sections; skip non-applicable items.

## Resources

### references/
`references/code-review-process.md` contains the full checklist and comment templates.
