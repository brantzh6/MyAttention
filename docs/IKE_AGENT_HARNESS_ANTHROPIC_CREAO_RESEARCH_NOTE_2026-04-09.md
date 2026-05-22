# IKE Agent Harness Anthropic CREAO Research Note

Date: 2026-04-09
Status: accept_with_changes

## Scope

This note records a narrow research pass on:

- Anthropic Claude agent/runtime documentation that is directly relevant to
  `agent harness`
- CREAO runtime/sandbox documentation that is directly relevant to isolated
  agent execution
- how those ideas map onto the current IKE harness/runtime direction

## Source Discipline

This note uses:

- official Anthropic Claude Code / Agent SDK docs
- official CREAO docs
- local repo inspection of current IKE/OpenClaw/Claude-worker harness work

If a term could not be directly confirmed in official docs, it is treated as
an external framing, not as a locked official product term.

## What Anthropic Official Docs Clearly Confirm

### 1. Anthropic has an agent runtime surface built around tools, permissions, sessions, and subagents

From the Claude Agent SDK overview:

- the SDK provides the same agent loop and context management that power
  Claude Code
- built-in tools include file read/write/edit, bash, web search, and web fetch
- permissions are first-class
- sessions are first-class
- subagents are first-class

Implication for IKE:

- the important architectural shape is not just “strong model”
- it is:
  - controlled tools
  - explicit permissions
  - session management
  - subagent separation
  - observability / control surfaces

### 2. Anthropic explicitly treats permissions as a first-class control plane

Official docs show:

- agents can be configured with bounded `allowed_tools`
- hooks can intercept and control agent behavior
- read-only patterns are explicitly supported

Implication for IKE:

- our current direction is right:
  - workspace isolation alone is not enough
  - tool/capability policy has to become part of the harness

### 3. Anthropic explicitly treats sessions as first-class context containers

Official docs show:

- sessions can be resumed
- sessions can be forked
- context continuity is not the same thing as global memory truth

Implication for IKE:

- our runtime truth model still matters
- but execution/session identity must be bound more tightly to delegated runs

### 4. Anthropic subagents have separate context and tool restrictions

Official docs show:

- subagents can be specialized
- subagents use separate context windows
- subagents can have different tool permissions

Implication for IKE:

- our controller/delegate split is directionally aligned
- but we still need stronger execution-boundary enforcement, not just role docs

## What CREAO Official Docs Clearly Confirm

### 1. Every chat thread runs in its own isolated sandbox

Official CREAO sandbox lifecycle docs state:

- each chat thread has its own isolated sandbox
- packages, files, and running processes persist within that thread
- work done in one thread does not affect another
- deleting a thread cleans up its sandbox

Implication for IKE:

- this is the clearest product proof of the “one execution thread, one isolated
  environment” pattern
- this is directly relevant to our move away from shared-root OpenClaw workspaces

### 2. CREAO separates thread sandbox persistence from agent-run environment reuse

Official CREAO docs state:

- a thread sandbox persists between messages in the same thread
- agent runs start from a saved environment snapshot
- environment updates are explicit and separately saved
- regular runs do not automatically write back into the environment snapshot

Implication for IKE:

- this is very important for us
- it suggests a three-part split:
  - task/run sandbox
  - reusable environment snapshot
  - runtime truth/state outside both

### 3. CREAO makes environment setup a first-class flow

Official CREAO docs state:

- agent environments can be updated explicitly
- packages, files, and configuration can be saved to the agent environment
- those setup sessions are distinct from normal runs

Implication for IKE:

- we should not mix:
  - ordinary delegated task execution
  - environment maintenance
  - runtime truth

## Local Repo Alignment Check

Current repo state is directionally aligned, but only partially implemented.

### Already aligned

- controller/delegate truth boundaries are explicit
- shared-root pollution has been materially reduced
- OpenClaw isolated workspaces now exist outside the repo root
- Claude worker run-root now exists outside the repo root
- runtime task/memory/decision truth is already distinguished from docs/chat

### Still missing

- true per-run sandbox enforcement
- first-class capability restrictions per lane/run
- guaranteed write boundaries per agent/run
- ephemeral workspace lifecycle
  - provision
  - bind task to sandbox
  - archive/teardown
- stronger binding between runtime task lease and actual execution workspace
- stronger detached completion / durable finalization for Claude worker

## Current Controller Judgment

### Strong conclusion

Anthropic + CREAO together strengthen, not weaken, our current direction:

- isolated execution surfaces are not optional
- agent harness is not just prompts and role files
- sandbox / permissions / session identity / environment lifecycle must become
  first-class operational rules

### Most important takeaway for IKE

The next evolution is not:

- broader agent autonomy

The next evolution is:

- controller-owned runtime truth
- agent-specific isolated workspaces
- bounded tools/permissions
- explicit environment lifecycle
- durable result / session / artifact closure

## Recommended Follow-up

1. Add a first-class `sandbox_identity` / `workspace_identity` concept to the
   execution harness.
2. Tighten Claude worker and OpenClaw execution capability policy.
3. Stop treating isolation as merely a directory layout concern.
4. Separate:
   - execution sandbox
   - reusable environment snapshot
   - runtime truth/state
5. Preserve broad integration discipline:
   - do not let agent environment persistence become runtime truth

## Sources

- Anthropic Agent SDK overview:
  - [https://code.claude.com/docs/en/agent-sdk/overview](https://code.claude.com/docs/en/agent-sdk/overview)
- CREAO Sandbox Lifecycle:
  - [https://docs.creao.ai/pro/sandbox-lifecycle](https://docs.creao.ai/pro/sandbox-lifecycle)
- CREAO Agent Runtime Environment:
  - [https://docs.creao.ai/pro/agent-runtime-environment](https://docs.creao.ai/pro/agent-runtime-environment)
- Local repo inspection:
  - `docs/PROJECT_AGENT_HARNESS_CONTRACT.md`
  - `docs/IKE_REPOSITORY_RESTRUCTURE_AND_WORKSPACE_ISOLATION_PLAN_2026-04-09.md`
  - `docs/IKE_REPOSITORY_RESTRUCTURE_PHASE1_RESULT_2026-04-09.md`
  - `services/api/claude_worker/worker.py`
  - `docs/IKE_RUNTIME_V0_TASK_STATE_AND_STORAGE_ARCHITECTURE.md`
