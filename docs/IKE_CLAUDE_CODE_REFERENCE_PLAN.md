# IKE Claude Code Reference Plan

## Purpose

`Claude Code` is no longer only a benchmark-adjacent case.
It is now a strategic technical reference for:

- agent engineering workflow
- memory and context handling
- task orchestration
- permissions and trust boundaries
- how IKE should think about its own engineering substrate

This plan defines how to study it without collapsing into uncontrolled copying.

## Why This Matters

The recent source exposure event makes `Claude Code` relevant in two distinct
ways:

1. as a world event IKE should have been able to capture
2. as a primary technical artifact whose implementation patterns may inform
   IKE's own architecture

The local repository at:

- `D:\claude-code`

is therefore a first-class study object.

## Evidence Roles

IKE should distinguish two local reference roles.

### 1. Primary Local Artifact

Path:

- `D:\claude-code`

Role:

- direct technical evidence
- actual architecture, tasks, memory, tools, and coordinator patterns

Strength:

- highest technical value for implementation understanding

Limit:

- requires careful controller interpretation
- may contain incidental or leaked details that are not universally reusable

### 2. Structured Secondary Interpretation

Path:

- `D:\code\MyAttention\.qoder\repowiki`

Role:

- structured repo explanation
- accelerated navigation aid
- map of subsystems and references

Strength:

- faster orientation
- useful summary of large codebases

Limit:

- not primary evidence
- may flatten nuance or miss critical implementation details

Controller rule:

- use repowiki to navigate and summarize
- use `D:\claude-code` to validate actual engineering patterns

## Main Questions

The study should answer:

1. which Claude Code patterns are genuinely reusable for IKE?
2. which ones are product-specific and should not be copied?
3. what does Claude Code do around:
   - context
   - memory extraction
   - tasks
   - coordinator/swarm
   - permissions
   - tool invocation
4. which of these patterns help IKE mainline gaps right now?

## First Study Areas

Prioritize these areas in `D:\claude-code\src`:

- `QueryEngine.ts`
- `context.ts`
- `tasks/`
- `coordinator/`
- `memdir/`
- `services/extractMemories/`
- `utils/permissions/`
- `tools/`

Use `.qoder/repowiki` to shorten orientation in:

- architecture overview
- task system overview
- context and memory overview
- service and backend structure

## Expected Outputs

The first study pass should produce:

1. subsystem map
   - Claude Code subsystem -> IKE layer/gap
2. reusable pattern list
   - what is worth adapting
3. non-transferable pattern list
   - what is product-specific or unsafe to imitate directly
4. mainline relevance mapping
   - which current IKE gaps may benefit
5. bounded follow-up packets
   - one packet per reusable pattern cluster

## Candidate Mapping Categories

Examples of likely mappings:

- Claude Code context handling -> IKE active work surface and working memory
- task system -> IKE research task / experiment / closure substrate
- memory extraction -> IKE memory and knowledge capture loops
- permissions model -> IKE governance and trust boundary controls
- coordinator/swarm -> IKE controlled delegation and multi-brain execution

These are hypotheses, not accepted truths.
They must be validated from code evidence.

## Constraints

Do not:

- copy architecture wholesale
- assume product behavior from summaries alone
- treat leaked code as normative best practice
- widen the study into a giant full-code audit

Do:

- keep packets bounded
- distinguish primary vs secondary evidence
- tie findings back to current IKE mainline gaps
- preserve truthful recommendation levels

## Success Condition

This plan succeeds when IKE can produce:

- a credible subsystem-to-subsystem mapping
- at least one concrete reusable engineering pattern
- at least one explicit rejection of a pattern that should not be copied
- a bounded study/prototype recommendation grounded in primary evidence

## Current Progress

Completed:

- `B1` subsystem mapping
- `B2` memdir study

Current strongest reusable cluster:

- `memdir`

Current next packet:

- `IKE procedural memory prototype implementation`
