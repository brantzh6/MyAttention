# IKE Runtime v0 Packet R2-B1 Coding Brief

## Packet

- `R2-B1`
- `First Real Task Lifecycle Proof`

## Goal

Produce one narrow, truthful runtime proof for a real task lifecycle through
the currently hardened runtime base.

## Scope

Stay inside:

- runtime task lifecycle helpers
- runtime task/decision/work-context/memory closure path
- focused runtime tests

Do not widen into:

- UI/API/platform work
- scheduler platform work
- benchmark multiplication

## Required Proof Shape

Demonstrate one task flowing through a truthful narrow lifecycle such as:

- inbox/start point
- ready
- active
- review/closure path
- done

The exact path may stay narrow, but it must be:

- runtime-owned
- auditable
- not dependent on hidden chat truth

## Acceptance Focus

1. task lifecycle truth is explicit
2. no hidden second truth source is introduced
3. the proof uses the hardened runtime base as it now exists
4. tests make the lifecycle proof auditable

## Required Output

1. summary
2. files_changed
3. why_this_solution
4. validation_run
5. known_risks
6. recommendation
