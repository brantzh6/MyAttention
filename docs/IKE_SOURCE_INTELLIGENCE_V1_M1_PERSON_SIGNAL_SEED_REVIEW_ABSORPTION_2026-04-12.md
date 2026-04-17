# IKE Source Intelligence V1 M1 Person Signal Seed Review Absorption

Date: 2026-04-12
Scope: `IKE_SOURCE_INTELLIGENCE_V1_M1_PERSON_SIGNAL_SEED_RESULT_2026-04-12`

## Review Inputs

- Claude: `accept`
- ChatGPT: `accept_with_changes`

## Controller Judgment

- code-level judgment: `accept`
- controller/project-level judgment: `accept_with_changes`

This slice is accepted as a bounded discovery-quality improvement, but it must
remain a seed-level enhancement and not expand into person-identity or
cross-source resolution work.

## Accepted Points

1. `signal -> person` seeding is the right bounded next slice after the
   `versions realism` lane was closed.
2. `author -> builder` is acceptable only because it remains conservative and
   weaker than `owner -> maintainer`.
3. The main remaining risk is not positive proof, but negative-boundary drift.

## Absorbed Follow-Up

One negative-boundary guardrail is accepted and applied immediately:

- author-derived person seeds do not escalate into `builder` outside
  `METHOD/FRONTIER`; under `LATEST`, they stay untyped and keep the default
  lower follow score

This makes the focus-bounded nature of the heuristic explicit in tests.

## Ongoing Boundary

This slice does not authorize:

1. cross-source person identity resolution
2. role escalation from `builder` to `maintainer`
3. person-graph or actor-graph expansion
4. a new person-discovery sub-mainline

Additional controller wording now fixed:

- `x.com/{handle}` and `twitter.com/{handle}` remain source-local person seeds
- they must not be merged or promoted into canonical person identity without a
  separately reviewed identity-resolution lane

## Stop Rule

This `person signal seed` slice is now considered closed for the current M1
scope.

Allowed continuation from this exact lane:

1. none by default

Future work may only reopen if it is explicitly framed and reviewed as one of:

1. negative-boundary hardening for accidental role escalation
2. separately scoped identity-resolution work
3. separately scoped cross-source merge work

Everything else should move to another bounded slice instead of extending this
seed lane in place.

## Recommendation

- `accept_with_changes`
