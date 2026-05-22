# Project Evolution Loop and Method Upgrade

## Purpose

This document defines the missing independent evolution leg in the current
project method.

The project already has:

- bounded implementation
- bounded review
- bounded testing

What it still lacks as a first-class system is:

- a stable mechanism for turning completed work into method improvement
- a stable rule for promoting reviewed findings into procedural memory
- a stable rule for preserving future-value review findings

This document defines that loop.

## 1. First Principle

Evolution is not:

- watchdog keepalive
- runtime restart logic
- generic review comments

In this project, evolution means:

- learning from repeated work
- tightening methods
- upgrading contracts
- reducing future drift

The evolution leg is not responsible for finishing the current task.
It is responsible for improving how future tasks are done.

## 2. Evolution Inputs

The evolution loop may consume:

- accepted packet reviews
- accepted_with_changes reviews
- test findings
- benchmark closures
- study closures
- repeated controller corrections
- repeated delegate failure patterns

The evolution loop must not treat these as equal.

Highest-value inputs:

- accepted closure artifacts
- controller-reviewed results
- repeated cross-review findings

Weak inputs:

- raw delegate output
- unreviewed summaries
- chat-only impressions

## 3. Evolution Outputs

The evolution loop should produce one or more of:

- `now_to_absorb`
- `future_to_preserve`
- procedural memory candidate
- contract change
- packet design change
- test matrix change
- benchmark method change
- runtime design backlog item

## 4. Promotion Rules

### Draft Observation

Use when:

- a pattern is seen once
- evidence is still weak

Allowed effect:

- note it
- do not change durable method yet

### Controller Correction

Use when:

- a specific packet or review needs immediate tightening

Allowed effect:

- update active brief/docs immediately

### Procedural Memory Candidate

Use when:

- a repeatable lesson emerges from reviewed work
- evidence is strong enough to reuse cautiously

Allowed effect:

- visible as candidate
- not yet default law

### Durable Method Upgrade

Use when:

- the pattern has survived review
- the lesson is reusable across multiple packets or cases
- controller accepts it as a project rule

Allowed effect:

- update harness contract
- update thinking/model method docs
- update starter kits if cross-project relevant

## 5. Evolution Roles

### Controller

Owns:

- durable method acceptance
- deciding whether an observation becomes project rule
- deciding whether a future idea enters the long-horizon backlog

### Evolution Review Agent

Owns:

- spotting repeated failure/correction patterns
- proposing contract/method upgrades
- grouping weak signals into candidate method changes

Does not own:

- final method acceptance

### Procedural Memory Agent

Owns:

- extracting candidate reusable lessons from accepted closures

Must not:

- invent lessons from weak or draft evidence

### Benchmark Governor

Owns:

- detecting benchmark theater
- checking whether benchmark conclusions outrun evidence quality

## 6. Mandatory Review Absorption

Every meaningful review must produce:

### now_to_absorb

Immediate constraints or corrections for the active packet/phase.

### future_to_preserve

Valuable directions that are not current-scope work but should not be lost.

This is mandatory.

If a review only changes the current packet and does not preserve future value,
the evolution loop is incomplete.

## 7. Closure-to-Memory Rule

A closure artifact may generate a procedural memory candidate only if:

- the closure is reviewed
- the payload is explicit
- upstream linkage is present
- the claimed lesson is not broader than the evidence

Do not derive durable memory from:

- draft closures
- fake summaries
- inferred intent that was not actually in the reviewed result

## 8. Method Upgrade Targets

The evolution loop may update:

- task packet design
- review checklists
- test validation matrix
- evidence hierarchy rules
- benchmark method frame
- runtime governance rules
- starter-kit cross-project guidance

It must not silently update:

- top-level project goal
- mainline priority
- architecture branch selection

These remain controller-only.

## 9. Current Project Upgrade Priorities

Immediate evolution priorities:

1. strengthen critical entity judgment
2. make testing a first-class independent leg
3. make benchmark evidence quality stronger than benchmark shape
4. make procedural memory truthful and narrowly promoted
5. reduce controller overload by improving packet, review, and validation
   structure

## 10. Long-Horizon Direction

Longer-term, IKE Runtime should carry explicit support for:

- closure events
- validation events
- review absorption
- procedural memory promotion states
- method-upgrade recommendations

Until then, this document and the durable backlog serve as the project-level
evolution bridge.
