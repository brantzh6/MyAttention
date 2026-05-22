# Delegation Brief Template

Use this template when handing a bounded task to another coding/review/research agent.

This is a control artifact, not a free-form note.

## Required Fields

```md
# Delegation Brief

task_id: delegated-xxx
title: One-line task title
task_type: implementation | review | analysis | validation
problem_type: short normalized label
priority: P0 | P1 | P2

## Why This Task Exists
- What mainline problem this task supports
- Why it is being delegated instead of handled in the main controller thread

## Goal
- The specific outcome expected from this task

## Scope
- File(s) allowed to change
- File(s) allowed to read
- Explicit out-of-scope items

## Inputs
- Brief background needed for the task
- Relevant live behavior / errors / examples
- Existing constraints or decisions already made

## Constraints
- What must not be changed
- Required patterns / architectural boundaries
- Safety / compatibility requirements

## Expected Output
- Patch summary
- Files changed
- Validation result
- Known risks
- Recommendation: accept | accept_with_changes | reject

## Validation
- Exact test / command / page check expected

## Stop Conditions
- When the delegate must stop and report instead of guessing

## Version / Context Refs
- Mainline doc(s)
- Progress/changelog refs if needed
```

## Example

```md
# Delegation Brief

task_id: delegated-source-ui-001
title: Make active source plans easier to distinguish from historical noise
task_type: implementation
problem_type: source_intelligence_surface
priority: P0

## Why This Task Exists
- The current source-intelligence surface is technically populated but still hard for users to interpret.
- This is bounded UI work that can be delegated without giving away mainline control.

## Goal
- Improve `settings/sources` so active plans and current signals stand out from historical noise.

## Scope
- Allowed to change:
  - `services/web/components/settings/sources-manager.tsx`
- Allowed to read:
  - `docs/CURRENT_MAINLINE_HANDOFF.md`
  - `services/api/routers/feeds.py`
- Out of scope:
  - backend API contracts
  - task model redesign

## Inputs
- Source plans already contain current/latest version, review times, item types, and gate status.
- User feedback: current page changes are not obvious enough.

## Constraints
- Do not change backend payloads.
- Do not redesign the whole app shell.
- Keep the patch narrow and easy to validate.

## Expected Output
- Patch summary
- Files changed
- Validation result
- Known risks
- Recommendation: accept | accept_with_changes | reject

## Validation
- `npx tsc --noEmit`
- open `http://127.0.0.1:3000/settings/sources`
- confirm active plans are visually distinct from historical/noisy ones

## Stop Conditions
- If backend data is insufficient and new API fields are required, stop and report.

## Version / Context Refs
- `docs/CURRENT_MAINLINE_HANDOFF.md`
- `docs/CONTROLLED_DELEGATION_STRATEGY.md`
```

## Acceptance Rule

No delegated result should be accepted unless it can be judged against:

- a bounded scope
- a concrete output
- a concrete validation path

If any of those are missing, the brief is incomplete.
