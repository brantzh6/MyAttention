# IKE Repository Restructure And Workspace Isolation Plan

Date: 2026-04-09
Status: proposed

## Why This Must Be Done

The current repository root at:

- `D:\code\MyAttention`

is serving too many roles at once:

- product source tree
- controller working tree
- OpenClaw agent workspace
- Claude worker artifact store
- runtime/delegation artifact store
- long-lived experimental memory surface

This makes the workspace increasingly hard to audit and increases the risk of:

- accidental source-tree pollution
- ambiguous ownership of generated files
- unstable review signals
- path drift across automation and agents
- future migration cost increasing over time

## Current Truthful Classification

### A. Project-core source and durable project docs

These belong to the actual product repository and should remain in the future
canonical project root:

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
- `README.md`
- `CHANGELOG.md`
- `PROGRESS.md`
- `package.json`
- `pnpm-workspace.yaml`
- project entry helpers such as:
  - `manage.py`
  - `start.bat`
  - `runtime_watchdog.py`

### B. Controller / agent / runtime-operational artifacts

These are not product-core source. They are execution environment surfaces,
agent state, or generated artifacts:

- `.runtime/`
- `.openclaw/`
- `.codex/`
- `.qoder/`
- `.claude/`
- `memory/`
- `.pytest_cache/`
- `__pycache__/`
- `.tmp/`

### C. Historical / persona / workspace-local metadata

These may be useful locally but are not part of the core runtime/product
architecture:

- `HEARTBEAT.md`
- `IDENTITY.md`
- `SOUL.md`
- `TOOLS.md`
- `USER.md`
- `.acpxrc.json`

These should be explicitly reviewed during migration rather than silently moved.

## Proposed Target Structure

### Canonical product root

- `D:\code\IKE`

This becomes the new repository root and the only canonical product source tree.

### Execution / agent runtime root

Recommended:

- `D:\code\_ike-runtime`

This becomes the home for controller/agent/generated operational surfaces:

- `D:\code\_ike-runtime\openclaw\...`
- `D:\code\_ike-runtime\claude-worker\...`
- `D:\code\_ike-runtime\delegation\...`
- `D:\code\_ike-runtime\logs\...`
- `D:\code\_ike-runtime\memory\...`

If the leading underscore is undesirable, use:

- `D:\code\IKE-runtime`

### Optional controller-local surface

If controller-local materials should remain separate from shared runtime
artifacts, add:

- `D:\code\_ike-controller`

This is optional and should not be introduced unless there is a clear controller
benefit.

## Recommended Migration Semantics

### What should move into `D:\code\IKE`

Move:

- all project-core source
- durable docs
- migrations
- scripts
- package manifests
- git history

### What should NOT remain inside the canonical repo root

Move out of the repo root over time:

- `.runtime/`
- `.openclaw/`
- `.codex/`
- `.qoder/`
- `.claude/`
- `memory/`

These are still important, but they should become external operational roots.

### What should remain ignored even after migration

- `.venv/`
- `.pytest_cache/`
- `__pycache__/`
- local temp logs

## Workspace Isolation Rules

### Controller

Controller should use the canonical project root:

- `D:\code\IKE`

but should not use that root as the default artifact dump for delegated lanes.

### OpenClaw agents

Current shared-root configuration is too risky.

Future state:

- no OpenClaw agent should use the canonical repo root as its default shared
  mutable workspace
- coder lane should use a dedicated worktree or isolated workspace
- reviewer lanes should use:
  - isolated workspaces
  - or explicitly constrained read/report surfaces

Recommended pattern:

- `D:\code\_ike-runtime\openclaw\workspaces\coder-qwen`
- `D:\code\_ike-runtime\openclaw\workspaces\reviewer-qwen`
- `D:\code\_ike-runtime\openclaw\workspaces\kimi-review`

### Claude worker

Claude worker should not keep its run store under the product repo.

Move:

- `D:\code\MyAttention\.runtime\claude-worker`

to something like:

- `D:\code\_ike-runtime\claude-worker`

This is important because Claude worker runs are:

- large
- durable
- operational
- not product source

## Rename Semantics

This is also a product rename step:

- old repository/root label: `MyAttention`
- future canonical project label: `IKE`

The rename should be treated explicitly, not as an incidental directory move.

That means:

1. repository root path changes
2. docs and launch guidance must be updated
3. agent workspace configs must be updated
4. path-sensitive scripts must be reviewed

## Backup Requirements Before Any Move

This migration must not start without all three backup layers.

### 1. Git checkpoint

Create a dedicated pre-migration branch and commit the current durable state.

Example intent:

- `codex/pre-ike-restructure-2026-04-09`

### 2. Cold directory backup

Create a raw filesystem backup of the current tree:

- `D:\code\_backups\MyAttention-pre-ike-restructure-2026-04-09`

This backup must include ignored directories.

### 3. Agent/runtime backup

Create separate copies of:

- `.runtime/`
- `.openclaw/`
- `.codex/`
- `memory/`

These are important because they are not guaranteed to be fully preserved in git.

## Rollback Requirements

Rollback must be possible at three levels:

### A. Git rollback

Return to the pre-migration branch/commit.

### B. Directory rollback

Restore the cold filesystem backup if path migration breaks the workspace.

### C. Agent-config rollback

Restore previous OpenClaw / Claude / Codex runtime roots if new workspace
isolation breaks execution.

## Impact On Current Codex Thread

This matters.

Current thread context is heavily path-bound to:

- `D:\code\MyAttention`

If the directory is moved immediately in-place, the current thread will inherit
stale path references across:

- docs
- code references
- runtime references
- delegated artifact paths

So the safest sequence is:

1. prepare structure and backups first
2. create the new canonical root in parallel
3. update configs and launch paths
4. switch the active working context only after the new root is verified

Do NOT do a blind in-place rename first.

## Recommended Execution Order

### Phase 1. Inventory freeze

- finalize classification of root directories
- mark what is project-core vs runtime-operational

### Phase 2. Backup and git checkpoint

- create pre-migration branch
- commit durable docs/state
- create cold backup

### Phase 3. Parallel root creation

- create `D:\code\IKE`
- copy project-core source tree there
- do not move runtime-operational directories yet

### Phase 4. Runtime root extraction

- create `D:\code\_ike-runtime`
- relocate `.runtime`, OpenClaw runtime state, Claude worker runs, memory

### Phase 5. Agent config rewrite

- update OpenClaw workspaces
- update Claude worker run roots
- update any path-sensitive scripts/docs

### Phase 6. Verification

- git status clean enough
- backend starts
- frontend starts
- runtime preflight works
- delegated lanes still run

### Phase 7. Controlled switchover

- make `D:\code\IKE` the canonical working root
- leave old `MyAttention` as fallback until stable

## Immediate Next Deliverables

The next concrete artifacts should be:

1. a migration inventory note
2. a backup-and-rollback checklist
3. an OpenClaw workspace rewrite plan
4. a Claude worker runtime-root rewrite plan

## Truthful Judgment

This restructure should proceed.

But it should proceed as:

- controlled migration
- with backup
- with rollback
- with parallel root creation first

not as an immediate in-place rename.
