# IKE Entity Discovery and Event Capture Method

## Purpose

This document defines the method IKE should use to identify:

- critical entities in emerging domains
- major events that matter to the project
- the evidence needed to justify research escalation

It exists because generic search adjacency is not enough.
The system must distinguish:

- who actually defines a concept
- who merely sits nearby in the ecosystem
- which events are world-important
- which events are relevant to IKE's mainline gaps

## Main Principle

Discovery must be wide first, then strict.

Do not:

- take top search results as truth
- assume GitHub rank alone defines importance
- treat media attention as concept authority

Do:

1. capture a wide candidate pool
2. extract entities and events
3. verify identity and authority
4. layer evidence
5. cross-reference relationships
6. produce structured confidence
7. escalate only when evidence supports it

## Two Distinct Targets

IKE should treat these as related but different tasks.

### 1. Entity Discovery

Goal:

- identify the people, organizations, repositories, communities, institutions,
  and artifacts that define or shape an emerging concept

Examples:

- maintainers
- project owners
- core contributors
- official organizations
- top communities
- leading labs or companies
- implementation repositories

### 2. Event Capture

Goal:

- detect significant world events that affect project priorities, trust
  boundaries, methods, or architecture

Examples:

- source leak
- major security incident
- official release with important capability change
- model/provider policy change
- benchmark scandal
- maintainer split or shutdown

## Step 1: Wide Candidate Capture

Start with a broad pool, not a conclusion.

Recommended first-pass sources:

- GitHub repositories, organizations, topics, maintainers
- official documentation sites
- company engineering blogs
- official release notes
- trusted media coverage
- expert commentary
- community discussions
- local primary artifacts
- structured repo interpretation layers

For an emerging topic, a reasonable first pass is:

- top 50 to 100 candidate signals

The purpose of this phase is recall, not precision.

## Step 2: Object Extraction

Do not rank links directly.
Extract structured objects from the candidate pool.

Minimum object types:

- `person`
- `organization`
- `repository`
- `community`
- `institution`
- `media`
- `event`
- `concept`
- `artifact`

For each object, preserve:

- canonical name
- source URL
- source type
- observed role
- why it was extracted

## Step 3: Identity and Authority Verification

Each entity must be checked before it is treated as important.

### Person checks

- maintainer or owner?
- recognized expert or practitioner?
- affiliated with a known organization or project?
- direct technical authorship visible?

### Organization checks

- official product/project owner?
- known company, lab, university, alliance, association, regulator, or think tank?
- direct involvement in the concept area?

### Repository checks

- active project or abandoned shell?
- direct implementation evidence?
- official repository or adjacent utility?
- visible maintainers, docs, issues, releases?

### Community checks

- central discussion venue or random mention surface?
- repeated references from serious practitioners?

Authority is not a single scalar.
At minimum track:

- `identity_confidence`
- `authority_confidence`
- `relevance_confidence`

## Step 4: Evidence Layering

Evidence must be layered before ranking.

Primary layers:

1. `authoritative_official`
2. `expert_maintainer`
3. `implementation_repository`
4. `community_discourse`
5. `media_context`

Additional technical layers:

6. `primary_local_artifact`
   - local codebase, docs, or source snapshot directly available for inspection
7. `structured_secondary_interpretation`
   - machine-generated but structured repo explanations, such as local repowiki
     layers

Rules:

- media alone cannot define the concept
- community alone cannot outrank official or maintainer evidence by default
- structured secondary interpretation cannot overrule primary artifacts
- local primary artifacts are high-value technical evidence, but still require
  controller interpretation

## Step 5: Cross-Reference Graph

Importance should be supported by relationships, not isolated mentions.

Useful relationships include:

- person maintains repository
- organization owns repository
- article cites repository
- maintainer mentions concept
- release references benchmark or method
- expert critiques another expert's interpretation
- artifact references another artifact

The system should ask:

- who cites whom?
- who implements what?
- who validates or disputes the concept?
- which sources independently converge on the same interpretation?

## Step 6: Confidence as Structured Judgment

Do not use one black-box score alone.

Minimum confidence dimensions:

- `identity_confidence`
- `authority_confidence`
- `concept_defining_confidence`
- `implementation_usefulness_confidence`
- `event_importance_confidence`
- `mainline_relevance_confidence`

An aggregate score may exist, but it must not be the only judgment.

## Step 7: Escalation Levels

Discovery should drive explicit escalation, not vague attention.

Recommended levels:

- `observe`
- `study`
- `prototype`
- `adopt_candidate`

Promotion requires increasingly strong evidence.

Examples:

- weak but interesting signals -> `observe`
- concept appears relevant but needs bounded study -> `study`
- direct reusable mechanisms found -> `prototype`
- repeated evidence plus successful validation -> `adopt_candidate`

## Event Capture Rules

Major events should be detected using multi-signal confirmation.

For important incidents, seek at least three of these:

- official statement
- direct technical artifact
- trusted media confirmation
- expert/security researcher confirmation
- community spread with concrete evidence

Examples:

- source-map leak
- security exposure
- forced takedown
- provider policy shift
- major release introducing new workflow capability

The event is not complete until IKE can answer:

1. what happened
2. what evidence supports it
3. why it matters to the project
4. which mainline gap it touches
5. whether it should trigger `observe`, `study`, `prototype`, or `adopt_candidate`

## Current Application

This method should now be applied to:

- `harness` benchmark entity correction
- `Claude Code` source exposure event capture
- `D:\claude-code` as a local primary technical artifact
- `.qoder/repowiki` as structured secondary interpretation

## Failure Modes To Avoid

- ranking by search position alone
- treating adjacency as authority
- treating media as concept-defining
- treating a skill catalog as method implementation
- treating local structured summaries as equal to primary code artifacts
- treating provisional event rumors as settled fact

## Success Condition

The method succeeds when IKE can do all of the following:

- identify the most important entities with reasons
- explain why those entities matter
- separate concept-defining from adjacent entities
- catch major events early enough to matter
- justify research escalation with layered evidence
- preserve a truthful path from signal to study to decision
