# OpenClaw Delegate Unique Session Protocol

Date: 2026-06-01
Status: enforced

## Incident

A concurrent `myattention-coder` dispatch failed with:

```text
EmbeddedAttemptSessionTakeoverError: session file changed while embedded
prompt lock was released
```

Root cause: multiple delegated turns reused the agent's default session,
causing session file collisions when concurrent executions attempted to
read/write the same session state.

## Rule

Every controller-authored delegated OpenClaw execution must include a
fresh explicit session UUID:

```powershell
openclaw agent --agent <id> --session-id <new-guid> --message <packet> ...
```

Do not reuse default sessions for bounded task packets. A session may be
resumed only when the controller explicitly intends continuation of the
same task.

## Rationale

OpenClaw agents persist session state to disk. When multiple delegated
turns share a default session:

1. Concurrent writes to the same session file corrupt state.
2. Prompt locks collide across unrelated task packets.
3. The embedded session takeover protection triggers, aborting runs.

Fresh UUIDs guarantee isolation between bounded task packets.

## Enforcement

- `ops/runners/registry.json` records this rule under `dispatch_rules`.
- Controllers must generate a new GUID per dispatch.
- **Required dispatch surface**: `scripts/ops/invoke_openclaw_delegate.ps1`
  - All controller-authored OpenClaw delegate dispatches MUST use this helper.
  - Direct openclaw.cmd invocation without session isolation is forbidden.
  - The helper provides: fresh GUID generation, resume authorization guard,
    safe argument escaping for messages with spaces, and dry-run mode.
  - **Quote boundary**: Messages containing embedded double quotes are rejected
    before launch. Controller packets should use quote-free message text
    pointing to file-backed task packets (e.g., "run packet from path/to/file.md").
    Spaces are supported and proven safe via live helper smoke.
- Review gates should check that packets include `--session-id` for
  delegated OpenClaw runs.
- This rule applies to all OpenClaw agent dispatches, regardless of
  target agent (ike-pm, ike-operator, myattention-coder, etc.).

## Exceptions

Session resumption is allowed only when:

1. The controller explicitly intends continuation of the same task.
2. The session ID is recorded in the packet with justification.
3. No other concurrent dispatch targets the same session.

## Related Documents

- `ops/runners/registry.json` - runner registry with dispatch_rules
- `docs/IKE_OPERATIONS_KERNEL_P0.md` - runner governance
- `docs/CONTROL_PLANE_SCHEDULING.md` - scheduling context
