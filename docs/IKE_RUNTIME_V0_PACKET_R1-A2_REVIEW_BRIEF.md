# IKE Runtime v0 Packet R1-A2 Review Brief

## Task ID

- `R1-A2`

## Goal

Review the `R1-A1` hardening implementation as a strict semantic and
truth-boundary review.

## Focus

Check for:

1. caller-discipline still masquerading as hard enforcement
2. fake trust through linkage-only checks
3. force-path escape hatches
4. scope creep beyond hardening
5. regression against first-wave guardrails

## Required Output

1. top findings
2. validation gaps
3. accept / accept_with_changes / reject recommendation
4. `now_to_absorb`
5. `future_to_preserve`

## Stop Conditions

Escalate if the patch introduces:

- fake durability
- hidden truth in JSONB or chat-only state
- delegate self-acceptance paths
- new broad architecture moves
