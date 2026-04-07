# Project Durable Recording and Git Discipline

## Purpose

This document defines when project knowledge must stop living in chat and be
written into durable project artifacts.

It also defines when milestone work must be archived into Git instead of
remaining only in the working tree.

This exists because:

- chat context is fragile
- local work can be lost by tool/runtime failure
- review findings are easy to forget when not written back
- uncommitted progress is not a reliable project memory system

## 1. Durable Recording Rule

Chat is not a durable system of record.

A decision, review, or method update must not remain only in chat when it is
any of the following:

1. changes active mainline direction
2. changes controller/delegate responsibilities
3. changes task/state/review/acceptance semantics
4. introduces a reusable method or benchmark rule
5. introduces a future-value finding that should not be lost
6. changes what the next milestone should be
7. records a real result from coding/review/testing/evolution

If any of the above is true, it must be written back into durable project
artifacts.

## 2. Minimum Durable Targets

Use the narrowest durable target that matches the content.

### Active operational truth

Write into:

- [D:\code\MyAttention\docs\CURRENT_MAINLINE_HANDOFF.md](/D:/code/MyAttention/docs/CURRENT_MAINLINE_HANDOFF.md)

Use for:

- current mainline
- current runtime phase
- latest controller judgment
- current next step

### Progress record

Write into:

- [D:\code\MyAttention\PROGRESS.md](/D:/code/MyAttention/PROGRESS.md)

Use for:

- meaningful completed progress
- milestone absorption
- executed packets

### Change history

Write into:

- [D:\code\MyAttention\CHANGELOG.md](/D:/code/MyAttention/CHANGELOG.md)

Use for:

- project-level capability changes
- architectural corrections already absorbed

### Method / design / review specifics

Write into:

- dedicated `docs/*.md`

Use for:

- design decisions
- review results
- benchmark conclusions
- packet briefs
- evolution outputs

### Long-horizon preservation

Write into:

- [D:\code\MyAttention\docs\IKE_LONG_HORIZON_BACKLOG_AND_DECISION_LOG.md](/D:/code/MyAttention/docs/IKE_LONG_HORIZON_BACKLOG_AND_DECISION_LOG.md)

Use for:

- valuable not-now items
- preserved future directions
- non-current but committed work

## 3. Mandatory Review Absorption

Every meaningful review must be absorbed in two layers:

1. `now_to_absorb`
   - immediately update active docs/briefs/rules

2. `future_to_preserve`
   - write into the long-horizon backlog or a durable review note

A review is incomplete if its future-value findings remain only in chat.

## 4. Git Discipline

Git is part of the memory system.
Uncommitted local files are not sufficient archival.

### Must reach Git at the next milestone

When a milestone meets any of the following:

1. cross-model review was completed
2. controller accepted a new stable phase judgment
3. packet cycle produced reviewed results
4. a reusable method/rule was stabilized
5. a runtime phase boundary moved forward

then the milestone should be archived to Git at the next safe checkpoint.

### Must not wait too long for Git

Do not leave the following only in working tree for extended time:

- major controller judgments
- review results that changed the mainline
- runtime design milestones
- durable benchmark results
- packet/result trees that future work depends on

## 5. Practical Git Rule for This Project

The project does not need a commit for every tiny chat conclusion.

But it should produce milestone-oriented commits when:

- a review milestone closes
- a packet wave becomes stable
- a new active mainline is established
- a new durable method/governance rule is accepted

## 6. Memory-System Urgency Rule

Because chat, local state, and uncommitted work are fragile, the memory system
is not optional future polish.

At current project maturity:

- runtime state durability
- reviewed result durability
- method durability
- Git archival discipline

must all be treated as part of the memory strategy.

This means:

- `IKE Runtime` memory/task kernel remains urgent
- reviewed closures should continue moving toward truthful memory candidates
- milestone archiving to Git should be treated as operational hygiene, not
  optional cleanup

## 7. Controller Reminder

When uncertain, prefer:

- writing the durable note now
- preserving the future item now
- archiving the stable milestone soon

instead of assuming the conversation history will still be available later.
