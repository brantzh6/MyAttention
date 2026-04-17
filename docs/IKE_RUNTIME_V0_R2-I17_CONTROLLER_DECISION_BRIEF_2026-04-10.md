# IKE Runtime v0 - R2-I17 Controller Decision Brief

Date: 2026-04-10
Phase: `R2-I17 Canonical Launch Baseline Alignment`
Type: `controller decision brief`

## Decision Requested

Should the current canonical Windows runtime service shape now be treated as
the accepted local controller-proof baseline for the current `R2-I` mainline?

## Short Answer

Recommendation:

- `accept_with_changes`

Meaning:

- accept the current canonical local `127.0.0.1:8000` service as the reviewed
  Windows local proof baseline
- accept that the current live promotable chain is the repo `uvicorn.exe`
  launch shape on Windows
- keep this acceptance narrow and explicitly confirmation-gated

## Evidence Chain

### 1. `R2-I14`

- [D:\code\MyAttention\docs\IKE_RUNTIME_V0_R2-I14_RESULT_MILESTONE_2026-04-10.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_R2-I14_RESULT_MILESTONE_2026-04-10.md)

What it established:

- controller-facing self-check can close code freshness truthfully
- reviewed Windows redirector semantics remain confirmation-gated

### 2. `R2-I15`

- [D:\code\MyAttention\docs\IKE_RUNTIME_V0_R2-I15_RESULT_MILESTONE_2026-04-10.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_R2-I15_RESULT_MILESTONE_2026-04-10.md)

What it established:

- there is now an explicit controller-facing decision inspect route above
  preflight
- the route keeps non-mutation and inspect-only boundaries explicit

### 3. `R2-I16`

- [D:\code\MyAttention\docs\IKE_RUNTIME_V0_R2-I16_RESULT_MILESTONE_2026-04-10.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_R2-I16_RESULT_MILESTONE_2026-04-10.md)

What it established:

- canonical `8000` can again be reclaimed onto the reviewed Windows redirector
  owner chain
- live controller decision returns:
  - `controller_confirmation_required`

### 4. `R2-I17`

- [D:\code\MyAttention\docs\IKE_RUNTIME_V0_R2-I17_RESULT_MILESTONE_2026-04-10.md](/D:/code/MyAttention/docs/IKE_RUNTIME_V0_R2-I17_RESULT_MILESTONE_2026-04-10.md)

What it established:

- the machine-readable `canonical_launch` surface is now aligned with the same
  Windows launch chain that is actually validated live
- live `canonical_launch.launch_mode = repo_uvicorn_entry`

## Current Technical Reading

The current live canonical Windows shape is now internally consistent:

- `code_freshness.status = match`
- `owner_chain.status = parent_preferred_child_mismatch`
- `repo_launcher.status = parent_and_child_repo_launcher_match`
- `windows_venv_redirector.status = windows_venv_redirector_candidate`
- `controller_acceptability.status = acceptable_windows_venv_redirector`
- `controller_promotion.status = controller_confirmation_required`
- `decision.recommended_action = controller_confirmation_required`
- `canonical_launch.launch_mode = repo_uvicorn_entry`

So the current remaining gap is no longer:

- route existence
- code freshness usability
- launch-baseline honesty

It is now mainly:

- whether the controller wants to treat this reviewed Windows shape as the
  accepted local baseline and advance the mainline above it

## What Accepting Means

If accepted, the controller is saying:

1. the current local canonical `8000` Windows redirector shape is sufficient as
   the reviewed local proof baseline
2. the current `R2-I` mainline no longer needs more launch-path clarification
   before the next narrow runtime step
3. `controller_confirmation_required` remains an explicit gate, not a silent
   promotion

## What It Does Not Mean

Acceptance does **not** mean:

- automatic controller acceptance mutation exists
- a durable controller-decision record already exists
- all owner mismatch states are acceptable
- non-Windows environments inherit the same exception
- detached supervision or scheduler semantics are solved

## Recommended Next Step After Acceptance

Advance to the next narrow runtime packet above the current live confirmed
shape, but keep it runtime-local and avoid drifting into:

- supervision
- daemonization
- scheduler semantics

## Recommendation

- `accept_with_changes`

Changes still remaining after acceptance:

1. keep the Windows redirector acceptance rule explicitly narrow
2. later decide whether controller acceptance should become a durable recorded
   action instead of remaining inspect-evidence-based
3. separately address the Windows console Unicode logging debt without folding
   it into this acceptance decision
