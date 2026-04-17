# Current Agent Harness Index

Date: 2026-04-10
Status: active support track

## Purpose

This is the compact entry file for the current agent-harness hardening track.

## Current Harness Goal

Make the routine execution chain:

- more auditable
- more bounded
- more consistent across lanes

without falsely claiming that full sandbox enforcement already exists.

## Current Practical Chain

- controller:
  - `GPT / Codex`
- routine automated lanes:
  - `Claude Code`
  - `OpenClaw`
  - `qoder`
- manual `Claude / Gemini / GPT`:
  - milestone or high-risk review only

## Current Reasoning Baseline

- OpenClaw:
  - `thinkingDefault = high`
- current routine default model preference:
  - latest `qwen3.6-plus`
- highest available automated reasoning is now the default for important delegated packets

## Current Materially Landed Metadata

- `lane`
- `reasoning_mode`
- `sandbox_identity`
- `sandbox_kind`
- `capability_profile`
- `write_scope`
- `network_policy`

These are now materially carried across the main automated lanes.

## Most Relevant Files

- contract:
  - [D:\code\MyAttention\docs\PROJECT_AGENT_HARNESS_CONTRACT.md](/D:/code/MyAttention/docs/PROJECT_AGENT_HARNESS_CONTRACT.md)
- boundary proof packet:
  - [D:\code\MyAttention\docs\IKE_AGENT_HARNESS_BOUNDARY_PROOF_PACKET_2026-04-11.md](/D:/code/MyAttention/docs/IKE_AGENT_HARNESS_BOUNDARY_PROOF_PACKET_2026-04-11.md)
- boundary proof checklist:
  - [D:\code\MyAttention\docs\IKE_AGENT_HARNESS_BOUNDARY_PROOF_CHECKLIST_2026-04-11.md](/D:/code/MyAttention/docs/IKE_AGENT_HARNESS_BOUNDARY_PROOF_CHECKLIST_2026-04-11.md)
- boundary proof result template:
  - [D:\code\MyAttention\docs\IKE_AGENT_HARNESS_BOUNDARY_PROOF_RESULT_TEMPLATE_2026-04-11.md](/D:/code/MyAttention/docs/IKE_AGENT_HARNESS_BOUNDARY_PROOF_RESULT_TEMPLATE_2026-04-11.md)
- boundary proof result:
  - [D:\code\MyAttention\docs\IKE_AGENT_HARNESS_BOUNDARY_PROOF_RESULT_2026-04-11.md](/D:/code/MyAttention/docs/IKE_AGENT_HARNESS_BOUNDARY_PROOF_RESULT_2026-04-11.md)
- enforcement plan:
  - [D:\code\MyAttention\docs\IKE_AGENT_HARNESS_ENFORCEMENT_PLAN_2026-04-09.md](/D:/code/MyAttention/docs/IKE_AGENT_HARNESS_ENFORCEMENT_PLAN_2026-04-09.md)
- capability matrix:
  - [D:\code\MyAttention\docs\IKE_AGENT_HARNESS_CAPABILITY_MATRIX_2026-04-09.md](/D:/code/MyAttention/docs/IKE_AGENT_HARNESS_CAPABILITY_MATRIX_2026-04-09.md)
- sandbox metadata spec:
  - [D:\code\MyAttention\docs\IKE_AGENT_HARNESS_SANDBOX_METADATA_SPEC_2026-04-09.md](/D:/code/MyAttention/docs/IKE_AGENT_HARNESS_SANDBOX_METADATA_SPEC_2026-04-09.md)
- capability policy draft:
  - [D:\code\MyAttention\docs\IKE_AGENT_HARNESS_CAPABILITY_POLICY_DRAFT_2026-04-09.md](/D:/code/MyAttention/docs/IKE_AGENT_HARNESS_CAPABILITY_POLICY_DRAFT_2026-04-09.md)
- reasoning policy:
  - [D:\code\MyAttention\docs\IKE_AGENT_HARNESS_REASONING_POLICY_2026-04-09.md](/D:/code/MyAttention/docs/IKE_AGENT_HARNESS_REASONING_POLICY_2026-04-09.md)
- Claude Code provider switching:
  - [D:\code\MyAttention\docs\CLAUDE_CODE_PROVIDER_SWITCHING_NOTE_2026-04-10.md](/D:/code/MyAttention/docs/CLAUDE_CODE_PROVIDER_SWITCHING_NOTE_2026-04-10.md)

## Landed Result Sequence

- Claude metadata P1:
  - [D:\code\MyAttention\docs\IKE_AGENT_HARNESS_P1_CLAUDE_METADATA_RESULT_2026-04-09.md](/D:/code/MyAttention/docs/IKE_AGENT_HARNESS_P1_CLAUDE_METADATA_RESULT_2026-04-09.md)
- OpenClaw metadata P1:
  - [D:\code\MyAttention\docs\IKE_AGENT_HARNESS_P1_OPENCLAW_METADATA_RESULT_2026-04-09.md](/D:/code/MyAttention/docs/IKE_AGENT_HARNESS_P1_OPENCLAW_METADATA_RESULT_2026-04-09.md)
- qoder metadata P1:
  - [D:\code\MyAttention\docs\IKE_AGENT_HARNESS_P1_QODER_METADATA_RESULT_2026-04-10.md](/D:/code/MyAttention/docs/IKE_AGENT_HARNESS_P1_QODER_METADATA_RESULT_2026-04-10.md)
- highest reasoning default:
  - [D:\code\MyAttention\docs\IKE_AGENT_HARNESS_HIGHEST_REASONING_DEFAULT_RESULT_2026-04-10.md](/D:/code/MyAttention/docs/IKE_AGENT_HARNESS_HIGHEST_REASONING_DEFAULT_RESULT_2026-04-10.md)
- profile defaults P2:
  - [D:\code\MyAttention\docs\IKE_AGENT_HARNESS_P2_PROFILE_DEFAULTS_RESULT_2026-04-10.md](/D:/code/MyAttention/docs/IKE_AGENT_HARNESS_P2_PROFILE_DEFAULTS_RESULT_2026-04-10.md)
- write scope P3:
  - [D:\code\MyAttention\docs\IKE_AGENT_HARNESS_P3_WRITE_SCOPE_RESULT_2026-04-10.md](/D:/code/MyAttention/docs/IKE_AGENT_HARNESS_P3_WRITE_SCOPE_RESULT_2026-04-10.md)
- network policy P4:
  - [D:\code\MyAttention\docs\IKE_AGENT_HARNESS_P4_NETWORK_POLICY_RESULT_2026-04-10.md](/D:/code/MyAttention/docs/IKE_AGENT_HARNESS_P4_NETWORK_POLICY_RESULT_2026-04-10.md)
- sandbox identity P5:
  - [D:\code\MyAttention\docs\IKE_AGENT_HARNESS_P5_SANDBOX_IDENTITY_RESULT_2026-04-10.md](/D:/code/MyAttention/docs/IKE_AGENT_HARNESS_P5_SANDBOX_IDENTITY_RESULT_2026-04-10.md)

## Controller Judgment

This track is now beyond plain workspace isolation.
But it is still not valid to claim:

- hard write enforcement
- hard network isolation
- full sandbox lifecycle enforcement

Those remain future work.

Current next proof task:

- boundary-proof packet:
  - [D:\code\MyAttention\docs\IKE_AGENT_HARNESS_BOUNDARY_PROOF_PACKET_2026-04-11.md](/D:/code/MyAttention/docs/IKE_AGENT_HARNESS_BOUNDARY_PROOF_PACKET_2026-04-11.md)
- current proof result:
  - [D:\code\MyAttention\docs\IKE_AGENT_HARNESS_BOUNDARY_PROOF_RESULT_2026-04-11.md](/D:/code/MyAttention/docs/IKE_AGENT_HARNESS_BOUNDARY_PROOF_RESULT_2026-04-11.md)
  - current truthful state:
    - external artifact landing is now also proven
    - hard sandbox enforcement remains unproven
- current live real-run gap:
  - [D:\code\MyAttention\docs\IKE_CLAUDE_WORKER_REAL_RUN_GAP_2026-04-11.md](/D:/code/MyAttention/docs/IKE_CLAUDE_WORKER_REAL_RUN_GAP_2026-04-11.md)
  - current truthful state:
    - real prompt delivery and detached durable finalization are not yet
      proven
- next narrow packet:
  - [D:\code\MyAttention\docs\IKE_CLAUDE_WORKER_P1_CROSS_PLATFORM_HARDENING_PACKET_2026-04-11.md](/D:/code/MyAttention/docs/IKE_CLAUDE_WORKER_P1_CROSS_PLATFORM_HARDENING_PACKET_2026-04-11.md)
  - [D:\code\MyAttention\docs\IKE_CLAUDE_WORKER_P1_CODING_BRIEF_2026-04-11.md](/D:/code/MyAttention/docs/IKE_CLAUDE_WORKER_P1_CODING_BRIEF_2026-04-11.md)
  - [D:\code\MyAttention\docs\IKE_CLAUDE_WORKER_P1_IMPLEMENTATION_TASK_PACKET_2026-04-11.md](/D:/code/MyAttention/docs/IKE_CLAUDE_WORKER_P1_IMPLEMENTATION_TASK_PACKET_2026-04-11.md)
  - [D:\code\MyAttention\docs\IKE_CLAUDE_WORKER_P1_DELIVERY_PACK_2026-04-11.md](/D:/code/MyAttention/docs/IKE_CLAUDE_WORKER_P1_DELIVERY_PACK_2026-04-11.md)
- current result:
  - [D:\code\MyAttention\docs\IKE_CLAUDE_WORKER_P1_RESULT_2026-04-11.md](/D:/code/MyAttention/docs/IKE_CLAUDE_WORKER_P1_RESULT_2026-04-11.md)
