# IKE Task Closure Plan

## Purpose

The system can now produce a bounded research trigger packet.

That is not enough.

A real intelligence loop also needs a clear closure path:

- the task runs
- the task result is written back
- the result informs a decision
- the decision updates the project's understanding

## Why This Exists

Without task closure, trigger packets are only:

- better TODOs
- better prompts
- better bounded study instructions

They are not yet:

- knowledge updates
- evolution decisions
- project-moving artifacts

## Task Closure Goal

For a bounded study or prototype task, the system should be able to answer:

1. what was inspected
2. what was found
3. what claims are now supported or rejected
4. whether the concept should move to:
   - continue observing
   - further study
   - prototype
   - reject / defer

## Required Closure Outputs

The first closure-capable path should eventually produce:

1. `study result`
   - what sources/artifacts were inspected
   - what was learned

2. `claim updates`
   - explicit supported / unsupported findings

3. `decision`
   - continue observing
   - continue study
   - prototype
   - reject / defer

4. `harness case / evaluation record`
   - did the bounded research packet actually close the loop?

## First Closure Target

The first closure target should be:

- `harness`

using the current bounded study packet:

- inspect implementation-relevant repositories
- determine applicability to project evaluation needs

## Guardrails

Task closure should not:

- pretend a study is complete when repository contents were not really inspected
- turn every study into a prototype candidate
- bury uncertainty behind a fake confidence number

## Immediate Next Steps

The next bounded design packets should define:

1. `study result` object shape
2. `decision handoff` shape
3. minimal closure path from:
   - `trigger packet`
   - to `study result`
   - to `Decision`
   - to `HarnessCase`
