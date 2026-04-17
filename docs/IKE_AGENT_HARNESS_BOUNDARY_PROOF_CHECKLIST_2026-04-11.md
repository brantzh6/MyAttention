# IKE Agent Harness Boundary Proof Checklist

Date: 2026-04-11
Status: controller checklist

## Purpose

Turn the harness boundary-proof packet into a concrete validation checklist.

## Checklist

### A. Workspace boundary

- verify current OpenClaw routine workspaces are outside:
  - `D:\code\MyAttention`
- verify routine delegated paths resolve to isolated roots
- record the exact roots observed

### B. Artifact boundary

- verify Claude worker default run artifacts land outside:
  - `D:\code\MyAttention`
- verify durable run artifacts are written under the external runtime root
- record the exact run-root observed

### C. Metadata coverage

For each main automated lane, verify durable artifact or packet coverage for:

- `lane`
- `reasoning_mode`
- `sandbox_kind`
- `capability_profile`
- `write_scope`
- `network_policy`
- `sandbox_identity`

Lanes:

- Claude worker
- OpenClaw
- qoder

### D. Enforcement honesty

Verify that the final proof result explicitly states these are still unproven
or not yet hard-enforced:

- hard write blocking
- hard network blocking
- per-run sandbox lifecycle isolation
- runtime-bound capability enforcement

### E. Final proof result

The proof note must include:

1. claimed boundary
2. proven boundary
3. unproven boundary
4. next hardening step

## Recommendation

`accept`

This checklist is the preferred validation shape for the current harness
boundary-proof packet.
