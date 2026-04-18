# IKE Worker Skill Import And Validation Spec

Date: 2026-04-18
Status: controller spec

## Purpose

Define how the IKE harness imports a worker skill from a versioned source and
validates it before execution.

This is the harness-side counterpart to the worker skill contract.

## Core rule

IKE may consume worker code from GitHub, but it must do so through a
versioned, reviewable, fail-closed import path.

The harness is the trust gate.

The worker package is an evidence-bearing input.

## Required package shape

A worker skill package should include at least:

- a manifest file
- a worker entrypoint
- durable docs describing the worker contract
- a bounded result protocol
- optional tests or smoke instructions

## Manifest role

The manifest is the machine-readable entry point for the harness.

It should declare:

- skill identity
- version / ref
- entrypoint
- supported execution modes
- model switching interface
- provider / model requirements
- artifact contract
- trust boundary
- validation hooks

The manifest is not the whole skill.

It is the minimum import surface.

## Import flow

The harness should follow this order:

1. fetch the skill package from a pinned GitHub ref or tagged release
2. read the manifest
3. validate required manifest fields
4. validate the declared capability shape against IKE policy
5. confirm the worker supports the required execution mode
6. confirm the worker supports the required model-switching contract
7. only then start execution

If any validation step fails, the harness must stop closed.

## Validation checks

At minimum, the harness should verify:

- identity matches the expected worker
- version/ref is pinned and reviewable
- manifest syntax is valid
- entrypoint exists
- supported execution modes include the requested mode
- model selection fields are present
- result schema is readable by controller
- trust boundary is explicit
- stop conditions are declared

## Required model-switching validation

The harness must not treat model choice as an internal worker mystery.

It should be able to see:

- default model
- supported models/providers
- selected model/provider for this packet
- whether override was requested
- whether the selected model is allowed

This is part of the worker skill contract, not a separate ad hoc setting.

## Result handling

After execution, the harness should project:

- durable artifacts
- selected model/provider
- execution mode
- prompt delivery evidence when relevant
- final recommendation

The worker output remains candidate evidence until controller review.

## Non-goals

- do not create a marketplace
- do not add auto-discovery
- do not bypass review gates
- do not let the worker become controller
- do not silently execute from mutable branches without a reviewable ref

## Relation to IKE

This spec lets IKE treat worker skills as imported capabilities.

That is the right shape for:

- `claude-worker`
- future worker implementations
- future multi-agent coordination on top of the same contract

