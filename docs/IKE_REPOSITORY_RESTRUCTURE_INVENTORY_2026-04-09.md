# IKE Repository Restructure Inventory

Date: 2026-04-09
Status: draft inventory for migration

## Keep In Canonical Project Root

Future canonical root:

- `D:\code\IKE`

Keep in that root:

- `config/`
- `docs/`
- `infrastructure/`
- `migrations/`
- `packages/`
- `scripts/`
- `services/`
- `skills/`
- `.gitignore`
- `AGENTS.md`
- `CHANGELOG.md`
- `PROGRESS.md`
- `README.md`
- `package.json`
- `pnpm-workspace.yaml`
- `manage.py`
- `start.bat`
- `runtime_watchdog.py`
- `check_cats.py`
- `feeds_test.json`

## Move Out Of Canonical Project Root

Move to external runtime/agent roots:

- `.runtime/`
- `.openclaw/`
- `.codex/`
- `.qoder/`
- `.claude/`
- `memory/`

## Local / Disposable / Regenerable

These should not drive repository structure decisions:

- `.pytest_cache/`
- `__pycache__/`
- `.tmp/`
- `.venv/`
- `services/web/tsconfig.tsbuildinfo`

## Review Before Keeping

These are workspace-local or identity/meta files and should be explicitly
reviewed during migration:

- `.acpxrc.json`
- `HEARTBEAT.md`
- `IDENTITY.md`
- `SOUL.md`
- `TOOLS.md`
- `USER.md`

## Current High-Risk Shared Roots

These are the main contamination points today:

- OpenClaw agents using:
  - `D:\code\MyAttention`
- Claude worker runs under:
  - `D:\code\MyAttention\.runtime\claude-worker`
- controller docs and generated runtime artifacts mixed under the same root

## Immediate Migration Interpretation

The migration should treat:

- project-core source
- runtime-operational surfaces
- controller-local metadata

as three different classes, not one monolithic repository tree.
