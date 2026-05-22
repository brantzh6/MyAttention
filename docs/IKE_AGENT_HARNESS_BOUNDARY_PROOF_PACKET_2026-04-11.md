# IKE Agent Harness Boundary Proof Packet

Date: 2026-04-11
Status: controller packet

## Purpose

Turn the current harness claim boundary into one explicit proof packet.

This packet is not about adding more harness features first.

It is about proving exactly what the current harness does and does not enforce.

## Why This Packet Exists

The project already has:

- isolated workspaces
- external run roots
- shared metadata vocabulary
- reasoning defaults
- lane capability metadata

But the strategic gap is still real:

- declared isolation is not the same as proven isolation
- metadata is not the same as hard enforcement
- controller language can drift if the current claim boundary is not written
  explicitly

## Proof Goal

Produce one durable proof packet that answers:

1. what isolation is materially real today
2. what is only metadata/audit support today
3. what is not yet proven
4. what the next hardening step should be

## Required Proof Axes

### 1. Workspace boundary proof

Prove whether routine delegated lanes are now executing outside the controller
root by default.

### 2. Artifact boundary proof

Prove whether delegated run artifacts land outside the shared project root by
default.

### 3. Metadata coverage proof

Prove which lanes now materially carry:

- `lane`
- `reasoning_mode`
- `sandbox_kind`
- `capability_profile`
- `write_scope`
- `network_policy`
- `sandbox_identity`

### 4. Enforcement honesty proof

State explicitly which of these are not yet hard-enforced:

- write blocking
- network blocking
- per-run sandbox lifecycle isolation
- runtime-bound capability enforcement

## Preferred Output

The proof result should be one concise durable note with:

1. claimed boundary
2. proven boundary
3. unproven boundary
4. next hardening step

## Non-Goals

- no new sandbox runtime
- no broad execution rewrite
- no fake claim that metadata equals enforcement
- no vague future-thinking without current evidence

## Recommendation

`accept`

This packet should be completed before the harness line claims stronger
sandboxing than it currently proves.
