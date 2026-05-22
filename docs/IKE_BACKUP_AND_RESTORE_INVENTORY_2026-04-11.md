# IKE Backup And Restore Inventory

Date: 2026-04-11
Status: controller baseline

## Purpose

Define the minimum asset inventory that must be recoverable for release and
rollback discipline to be real.

## Asset Classes

### 1. Code

Recoverable via:

- git branch
- git commit
- git tag

Minimum requirement:

- every accepted milestone has a recoverable pointer

### 2. Config

Includes:

- runtime process config
- provider routing
- model defaults
- agent contracts
- deployment templates

Minimum requirement:

- effective config must be versioned in project files or a tracked config repo

### 3. Database

Includes at least:

- Postgres runtime truth
- user/content state where relevant

Minimum requirement:

- pre-risk backup or restore point for:
  - schema changes
  - release promotions
  - environment cutovers

### 4. Cache / Queue

Includes:

- Redis operational state if relevant to current release

Minimum requirement:

- know whether Redis is disposable cache or rollback-relevant state
- do not leave this ambiguous

### 5. Vector / Knowledge Store

Includes:

- Qdrant or other vector storage
- environment-specific collections

Minimum requirement:

- know snapshot path or recreation strategy
- environment identity must be explicit

### 6. Runtime Artifacts

Includes:

- run logs
- proof artifacts
- worker run artifacts
- review bundle artifacts

Minimum requirement:

- store path must be known
- artifact retention must not depend on chat memory alone

## Current Immediate Gaps

As of this baseline, the project still needs more formal execution around:

1. staging/prod backup routines
2. vector snapshot discipline
3. explicit restore drills

## Controller Rule

If an asset is important enough to affect rollback, it must have either:

1. a backup path
2. a snapshot path
3. a deterministic recreation path

Otherwise rollback is incomplete.
