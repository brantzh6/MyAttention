# IKE Runtime v0 R1-F Execution Pack

## Review Prompt

Review `R1-F` as the next narrow runtime phase after materially complete
`R1-E`.

Focus on:

1. whether the proposed read surface stays runtime-derived
2. whether it avoids introducing persistent duplicate summary state
3. whether it stays helper-level instead of widening into broader UI/API work

Be especially critical about:

- hidden second truth sources
- summary state drifting away from runtime truth
- premature controller-facing surface expansion

## Packet Order

1. `R1-F1` coding
2. `R1-F2` review
3. `R1-F3` testing
4. `R1-F4` evolution

## Current Controller Judgment

- `R1-E` is materially complete with fallback review coverage
- the next preserved gap is controller-facing read usability, not pointer truth
- `R1-F` should remain helper-level and truth-derived

## Non-Negotiable Guardrails

- do not create a persistent duplicate summary object
- do not open broad UI/API rollout
- do not add new runtime object families
- do not mix benchmark/runtime work here
