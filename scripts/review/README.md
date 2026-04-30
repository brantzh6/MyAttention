# Review Runner

`run_l1_review.py` prepares deterministic local review artifacts for the project review cadence.

## Default L1 Prepare-Only Flow

```powershell
python D:\code\MyAttention\scripts\review\run_l1_review.py `
  --cwd D:\code\MyAttention `
  --task-id IKE_EXAMPLE_REVIEW `
  --title "Review bounded patch" `
  --target-brief docs\packet.md `
  --target-result docs\result.md `
  --validation "python -m pytest ..."
```

The default execution mode is `--execute none`. It writes artifacts only and does not launch a delegate.

Artifacts are written under:

- `.runtime\reviews\briefs\<task-id>.md`
- `.runtime\reviews\contexts\<task-id>.md`
- `.runtime\reviews\results\<task-id>.md`
- `.runtime\reviews\done\<task-id>.json`

The done JSON records artifact identity plus minimal attempt status:

- `status`
- `execute`
- `delegate_attempted`
- `delegate_command`
- `delegate_exit_code`

## Delegated Execution

Use `--execute qoder` to write artifacts and then call the existing Qoder review wrapper:

```powershell
python D:\code\MyAttention\scripts\review\run_l1_review.py `
  --cwd D:\code\MyAttention `
  --task-id IKE_EXAMPLE_REVIEW `
  --title "Review bounded patch" `
  --target-brief docs\packet.md `
  --target-result docs\result.md `
  --execute qoder
```

Use `--execute openclaw` to write artifacts and then call the existing OpenClaw review wrapper:

```powershell
python D:\code\MyAttention\scripts\review\run_l1_review.py `
  --cwd D:\code\MyAttention `
  --task-id IKE_EXAMPLE_REVIEW `
  --title "Review bounded patch" `
  --target-brief docs\packet.md `
  --target-result docs\result.md `
  --execute openclaw
```

The runner prints delegate stdout/stderr, records the delegate exit code, and returns non-zero when the delegate wrapper fails. It does not parse reviewer judgment, promote work, or make reviewer output authoritative.

Delegated execution is bounded by `--delegate-timeout`, which defaults to `1800` seconds. When the wrapper exceeds this limit, the runner prints `delegate_status: timeout`, emits controller-readable stderr/status, records a non-zero delegate exit code, and returns non-zero without parsing reviewer judgment or promoting the work.

## Level Rules

- `L1` is the default daily delegated review lane and creates no zip or external packet.
- `L2` prints GitHub PR / Codex review guidance and creates no external zip.
- `L3` must be requested with `--level L3` and only reminds the controller of the 10-entry zip rule.

Use `--dry-run` to print planned artifact paths and execution intent without writing files or launching delegates, even when `--execute qoder` or `--execute openclaw` is set.
