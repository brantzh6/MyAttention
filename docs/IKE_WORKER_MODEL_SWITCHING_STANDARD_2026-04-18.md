# IKE Worker Model Switching Standard

Date: 2026-04-18
Status: controller standard

## Purpose

Define a portable model-switching contract for all IKE worker skills.

The point is not to privilege Claude Code. The point is to make model choice
a first-class worker capability so IKE can support multiple models by design.

## Why this exists

IKE should not be locked to a single model. It should support:

- routine lanes
- stronger reasoning lanes
- backend-heavy lanes
- review lanes
- future worker variants

That means model switching must live in the worker skill contract, not only in
operator notes or Claude-specific setup.

## Existing mechanism materials

### Claude Code provider switching note

The current operator note records a manual Claude Code provider flow:

- routine lane: `qwen3.6`
- stronger backend lane: `glm-5.1`
- routine provider family can also switch between alternate models

This is the concrete reference for current operator practice.

Reference:

- [CLAUDE_CODE_PROVIDER_SWITCHING_NOTE_2026-04-10.md](/D:/code/MyAttention/docs/CLAUDE_CODE_PROVIDER_SWITCHING_NOTE_2026-04-10.md)

### Claude worker capability packet

The current Claude worker capability already exposes model selection
semantics:

- default model exists
- `--model` can override the default
- model is recorded in the worker packet and result protocol
- execution mode stays separate from model choice

That is the right shape for a reusable worker skill.

Reference:

- [IKE_CLAUDE_CODE_CAPABILITY_P2_CONTEXT_2026-04-17.md](/D:/code/MyAttention/docs/IKE_CLAUDE_CODE_CAPABILITY_P2_CONTEXT_2026-04-17.md)
- [IKE_CLAUDE_CODE_CAPABILITY_P2_TASK_PACKET_2026-04-17.md](/D:/code/MyAttention/docs/IKE_CLAUDE_CODE_CAPABILITY_P2_TASK_PACKET_2026-04-17.md)

## Standard requirement

Every worker skill in IKE must provide the same model-switching interface.

Provider backends may differ. The contract shape should not.

### Required worker-skill fields

At minimum, a worker skill must expose:

- `default_model`
- `supported_models`
- `supported_providers`
- `selected_model`
- `selected_provider`
- `reasoning_mode` when relevant
- `execution_mode`
- `model_override` support
- model provenance in result artifacts

### Required harness behavior

The IKE harness must be able to:

1. list the worker's supported model options
2. select a default model
3. override the model for a specific packet
4. validate that the chosen model is supported
5. record the selected model/provider in durable artifacts
6. surface the chosen model/provider back to controller review

### Required packet semantics

Each worker packet should be able to carry:

- `provider`
- `model`
- `reasoning_mode`
- `execution_mode`

The worker may map those fields differently per provider, but the packet
shape must remain portable.

## Non-negotiable rules

- do not encode a single model forever
- do not hide model choice inside worker internals
- do not let the worker silently swap models without provenance
- do not make model switching a Claude-only special case
- do not let the harness lose the selected model/provider on the way to
  review

## Relation to IKE

This standard belongs to the IKE worker skill layer.

It is not the IKE product identity.

It is a reusable execution capability that IKE should require from all
workers so the system can remain multi-model by design.

