# SDD in This Repo

SDD specs live under:

- `meta/sdd/specs/{pending,active,completed}/`

## Always Use The Wrapper

SDD auto-detects a root `specs/` directory. In this repo, specs are under `meta/`, so you must use
the wrapper script:

```bash
meta/tools/sdd <command> [args...]
```

Note: a repo `pre-commit` hook rejects commits that re-introduce legacy roots (`specs/`, `.memory_bank/`).
In particular, it blocks SDD-style `specs/{pending,active,completed}/` so SDD specs stay under `meta/`.

Examples:

```bash
meta/tools/sdd find-specs --json
meta/tools/sdd list-specs --json
meta/tools/sdd task-info --spec "meta/sdd/specs/active/<spec>.json" --json
```

## Cross-linking (Recommended)

For non-trivial work, keep MD and JSON specs connected:

- Work item spec (MD): add `SDD Spec: meta/sdd/specs/...json`
- SDD spec (JSON): set `metadata.work_item_spec` to the work item spec path

## Validation Notes

- `meta/tools/sdd` exports `CLAUDE_SDD_SCHEMA_CACHE=meta/sdd/schema` to make schema discovery stable across environments.
- Some `sdd validate` checks may be skipped with a warning if the optional `jsonschema` dependency is not installed in the `sdd` runtime.
